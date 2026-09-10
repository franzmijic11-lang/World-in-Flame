# Static check: does any country start the 1936 game over its battalion cap?
#
# Reads the scenario the way the game does - vanilla history with this mod's
# files layered on top - and applies the cap formula from
# common/scripted_effects/wif_battalion_cap.txt by hand.
#
# WHAT IT CANNOT SEE, and why the answer is a floor rather than an exact figure:
#   - Wartime bonuses. Only Italy and Ethiopia are at war on day one, and every
#     wartime source is POSITIVE, so ignoring them can only understate a cap.
#     A country reported as over IS over; a country at war may have headroom
#     this script does not credit it with.
#   - World tension is 0 at game start, so that band pays nothing anyway.
#   - Faction leader is worth +50%, and no faction exists at game start.
#   - Laws assigned inside has_dlc blocks. Where a country's history mentions
#     more than one conscription or economy law the row is marked rather than
#     guessed, and the most generous reading is used - again, understating who
#     is over rather than overstating it.

import os
import re
import glob
import collections

V = r"D:\Steam\steamapps\common\Hearts of Iron IV"
M = r"C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen"


def read(path):
    return re.sub(r"#.*", "", open(path, encoding="utf-8-sig", errors="replace").read())


def body_at(txt, start):
    """Return the {...} block beginning at index start (which must be a '{')."""
    depth = 0
    for i in range(start, len(txt)):
        if txt[i] == "{":
            depth += 1
        elif txt[i] == "}":
            depth -= 1
            if depth == 0:
                return txt[start:i + 1]
    return txt[start:]


# ------------------------------------------------------------------ majors
# is_major is bookmark membership: a country card without "minor = yes".
bookmark = read(os.path.join(V, "common", "bookmarks", "the_gathering_storm.txt"))
majors = set()
for m in re.finditer(r'"?([A-Z]{3})"?\s*=\s*\{', bookmark):
    block = body_at(bookmark, m.end() - 1)
    if ("ideology" in block or "history" in block) and not re.search(r"minor\s*=\s*yes", block):
        majors.add(m.group(1))

# ------------------------------------------------------------ map and states
urban = set()
for line in open(os.path.join(V, "map", "definition.csv"), encoding="latin-1"):
    f = line.strip().split(";")
    if len(f) >= 7 and f[6] == "urban":
        urban.add(int(f[0]))


def parse_state(path):
    t = read(path)
    m = re.search(r"\bid\s*=\s*(\d+)", t)
    if not m:
        return None
    pm = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
    om = re.search(r"\bowner\s*=\s*([A-Z]{3})", t)
    # state-level manpower is the population state_population reads
    mp = re.search(r"^\s*manpower\s*=\s*(\d+)", t, re.M)
    return int(m.group(1)), (
        [int(x) for x in pm.group(1).split()] if pm else [],
        om.group(1) if om else None,
        set(re.findall(r"add_core_of\s*=\s*([A-Z]{3})", t)),
        int(mp.group(1)) if mp else 0,
    )


states = {}
for path in glob.glob(os.path.join(V, "history", "states", "*.txt")):
    r = parse_state(path)
    if r:
        states[r[0]] = r[1]
modded_states = 0
for path in glob.glob(os.path.join(M, "history", "states", "*.txt")):
    r = parse_state(path)
    if r:
        modded_states += 1
        states[r[0]] = r[1]

# ------------------------------------------------------------ country history
CONSC = {
    "disarmed_nation": 0.0, "volunteer_only": 0.10, "limited_conscription": 0.15,
    "extensive_conscription": 0.25, "service_by_requirement": 0.35,
    "all_adults_serve": 0.45, "scraping_the_barrel": 0.50,
}
ECON = {
    "totaler_krieg_economy": 0.25, "war_economy": 0.20, "national_defense_state": 0.20,
    "wif_reichskommissariat_economy": 0.20, "tot_economic_mobilisation": 0.15,
    "partial_economic_mobilisation": 0.10, "new_economic_policy": 0.10,
    "capital_investment_model": 0.05, "low_economic_mobilisation": 0.0,
    "civilian_economy": -0.15, "isolation": -0.25, "undisturbed_isolation": -0.50,
}

country_file = {}
for path in glob.glob(os.path.join(V, "history", "countries", "*.txt")):
    country_file[os.path.basename(path)[:3]] = path
modded_countries = 0
for path in glob.glob(os.path.join(M, "history", "countries", "*.txt")):
    tag = os.path.basename(path)[:3]
    if tag in country_file:
        modded_countries += 1
    country_file[tag] = path

hist = {}
for tag, path in country_file.items():
    t = read(path)

    # A history file carries every bookmark, so cut it at the 1939 section.
    # Without this the 1939 order of battle is what gets read - Germany came
    # out with 122 divisions in 1936 - and the later bookmark's stability, war
    # support and laws would be read too. The 1936 values are the ones before
    # the first 1939 set_oob.
    cut = re.search(r'set_oob\s*=\s*"?[A-Z]{3}_19(3[7-9]|4\d)', t)
    if cut:
        t = t[:cut.start()]

    stab = re.findall(r"set_stability\s*=\s*([\d.]+)", t)
    ws = re.findall(r"set_war_support\s*=\s*([\d.]+)", t)
    hist[tag] = {
        "consc": [k for k in CONSC if re.search(r"\b%s\b" % k, t)],
        "econ": [k for k in ECON if re.search(r"\b%s\b" % k, t)],
        "stab": float(stab[0]) if stab else 0.5,
        "ws": float(ws[0]) if ws else 0.5,
        "oob": list(dict.fromkeys(re.findall(r'set_oob\s*=\s*"?([A-Za-z0-9_]+)"?', t))),
    }

# ------------------------------------------------------------ OOB battalions
def oob_path(name):
    for base in (M, V):
        p = os.path.join(base, "history", "units", name + ".txt")
        if os.path.exists(p):
            return p
    return None


def count_battalions(name):
    """Line battalions and division count in one OOB file. Support companies are
    excluded, exactly as the cap excludes them - only the regiments block counts."""
    path = oob_path(name)
    if not path:
        return None, None
    t = read(path)
    template_size = {}
    for m in re.finditer(r"division_template\s*=\s*\{", t):
        block = body_at(t, m.end() - 1)
        nm = re.search(r'name\s*=\s*"([^"]+)"', block)
        rm = re.search(r"regiments\s*=\s*\{", block)
        if nm and rm:
            regiments = body_at(block, rm.end() - 1)
            template_size[nm.group(1)] = len(re.findall(r"\{\s*x\s*=\s*\d+\s+y\s*=\s*\d+\s*\}", regiments))
    bats = divs = 0
    for m in re.finditer(r'division_template\s*=\s*"([^"]+)"', t):
        size = template_size.get(m.group(1))
        if size:
            bats += size
            divs += 1
    return bats, divs


# ------------------------------------------------------------------ the cap
def band(value, table):
    for threshold, payout in table:
        if value > threshold:
            return payout
    return 0.0


STAB_BANDS = [(0.8, 0.10), (0.6, 0.09), (0.4, 0.07), (0.2, 0.05)]
WS_BANDS = [(0.8, 0.70), (0.6, 0.50), (0.4, 0.30), (0.2, 0.10)]

owned = collections.defaultdict(list)
for sid, (provs, owner, cores, pop) in states.items():
    if owner:
        owned[owner].append(sid)

rows = []
for tag in sorted(owned):
    h = hist.get(tag)
    if not h:
        continue

    territory = 0.0
    for sid in owned[tag]:
        provs, owner, cores, pop = states[sid]
        cities = sum(1 for p in provs if p in urban)
        if tag in cores:
            if cities:
                territory += 2 + 0.5 * (cities - 1)
            else:
                territory += 0.5 if pop < 150000 else 1.0
        else:
            territory += 0.1

    ambiguous = len(set(h["consc"])) > 1 or len(set(h["econ"])) > 1
    pct = 0.0
    if h["consc"]:
        pct += max(CONSC[c] for c in h["consc"])
    if h["econ"]:
        pct += max(ECON[e] for e in h["econ"])
    pct += band(h["stab"], STAB_BANDS)
    pct += band(h["ws"], WS_BANDS)

    red_army = 0
    if "SOV_the_red_army_dynamic_modifier" in read(country_file[tag]):
        red_army = 216   # 432 after The Glory of the Red Army, not completed at start

    # Major power is flat battalions now, not a percentage of the base.
    major = 864 if tag in majors else 0

    cap = 324 * (1 + pct) + territory + red_army + major

    # The Millions of China doubles the finished figure, applied last.
    if tag in ("CHI", "PRC"):
        cap *= 2
    if len(owned[tag]) < 2:
        cap = 27.0
    cap = max(cap, 1.0)

    # Prefer an explicitly 1936 order of battle; fall back to whatever the file
    # names first. DLC variants (_nsb and friends) hold the same divisions, so
    # which of those wins does not change the count.
    bats = divs = 0
    candidates = [n for n in h["oob"] if "1936" in n] or h["oob"]
    for name in candidates:
        b, d = count_battalions(name)
        if b:
            bats, divs = b, d
            break

    rows.append({
        "tag": tag, "bats": bats, "divs": divs, "cap": cap, "terr": territory,
        "red_army": red_army,
        "pct": pct, "states": len(owned[tag]), "ambiguous": ambiguous,
        "major": tag in majors,
    })

# --------------------------------------------------------------------- report
print("majors from the 1936 bookmark : %s" % " ".join(sorted(majors)))
print("mod overrides layered on      : %d states, %d country files" % (modded_states, modded_countries))
print("countries holding territory   : %d\n" % len(rows))

over = [r for r in rows if r["bats"] > r["cap"]]
print("=" * 78)
print("OVER THE CAP AT GAME START: %d" % len(over))
print("=" * 78)
if over:
    print("%-5s %7s %6s %9s %9s %8s %7s" % ("TAG", "BATS", "DIVS", "CAP", "OVER BY", "TERR", "STATES"))
    for r in sorted(over, key=lambda r: r["bats"] - r["cap"], reverse=True):
        print("%-5s %7d %6d %9.1f %9.1f %8.1f %7d%s" % (
            r["tag"], r["bats"], r["divs"], r["cap"], r["bats"] - r["cap"],
            r["terr"], r["states"], "  law ambiguous" if r["ambiguous"] else ""))

print("\nTIGHTEST TEN STILL UNDER")
under = sorted([r for r in rows if r["bats"] and r["bats"] <= r["cap"]], key=lambda r: r["cap"] - r["bats"])[:10]
for r in under:
    print("%-5s %7d bats  cap %8.1f   %7.1f spare" % (r["tag"], r["bats"], r["cap"], r["cap"] - r["bats"]))

print("\nTEN LARGEST ARMIES")
for r in sorted(rows, key=lambda r: r["bats"], reverse=True)[:10]:
    print("%-5s %7d bats %4d divs   cap %8.1f  %s%s" % (
        r["tag"], r["bats"], r["divs"], r["cap"],
        "OVER" if r["bats"] > r["cap"] else "ok",
        "   (major)" if r["major"] else ""))

print("\nSMALLEST CAPS")
for r in sorted(rows, key=lambda r: r["cap"])[:8]:
    print("%-5s cap %8.1f   %2d state(s)   %d bats" % (r["tag"], r["cap"], r["states"], r["bats"]))
