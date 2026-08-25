"""Pre-flight map check for Welt in Flammen.

Run this BEFORE launching the game after ANY province or state edit:

    python tools/check_map.py

It resolves states and strategic regions the way the game does - vanilla first,
then this mod's overrides by FILENAME - and reports the failures that crash
HOI4 during map init with nothing useful in error.log:

  * two states claiming the same province
  * a state whose provinces span more than one strategic region
    (this is the one that bites: the median strategic region holds only
     3 states, so a move to a neighbouring state very often crosses a seam,
     and then map/strategicregions must be edited too)
  * a land province in no state, or in no region
  * a state referencing a province that does not exist
  * victory_points or province-level buildings pointing at a province the
    state no longer contains
  * duplicate state ids, usually caused by an override filename that does
    not match vanilla's exactly

Edit VANILLA and WORKSHOP below if the game ever moves.
"""

import os, re, glob, csv

G = r"D:\Steam\steamapps\common\Hearts of Iron IV"
M = r"C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen"


def effective(subdir):
    files = {}
    for f in glob.glob(os.path.join(G, subdir, "*.txt")):
        files[os.path.basename(f)] = (f, "vanilla")
    for f in glob.glob(os.path.join(M, subdir, "*.txt")):
        files[os.path.basename(f)] = (f, "WiF")
    return files


def txt(p):
    return re.sub(r"#[^\n]*", "", open(p, encoding="utf-8-sig", errors="replace").read())


# ---- provinces that actually exist -----------------------------------------
land = set()
allp = set()
with open(os.path.join(G, "map", "definition.csv"), encoding="utf-8-sig") as f:
    for row in csv.reader(f, delimiter=";"):
        if len(row) < 5 or not row[0].isdigit():
            continue
        pid = int(row[0])
        allp.add(pid)
        if row[4] == "land":
            land.add(pid)

# ---- states ----------------------------------------------------------------
p2s, s2p, s_src = {}, {}, {}
dupe_state_ids = []
seen_ids = {}
problems = []

for name, (path, src) in effective(r"history\states").items():
    t = txt(path)
    m = re.search(r"\bid\s*=\s*(\d+)", t)
    if not m:
        continue
    sid = int(m.group(1))
    if sid in seen_ids:
        dupe_state_ids.append((sid, seen_ids[sid], name))
    seen_ids[sid] = name
    pm = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
    provs = [int(x) for x in pm.group(1).split()] if pm else []
    s2p[sid] = provs
    s_src[sid] = (name, src)
    for p in provs:
        if p in p2s and p2s[p] != sid:
            problems.append("province {} is in BOTH state {} ({}) and state {} ({})".format(
                p, p2s[p], s_src[p2s[p]][0], sid, name))
        p2s[p] = sid

# ---- strategic regions ------------------------------------------------------
p2r, r2p, r_src = {}, {}, {}
for name, (path, src) in effective(r"map\strategicregions").items():
    t = txt(path)
    m = re.search(r"\bid\s*=\s*(\d+)", t)
    if not m:
        continue
    rid = int(m.group(1))
    pm = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
    provs = [int(x) for x in pm.group(1).split()] if pm else []
    r2p[rid] = provs
    r_src[rid] = (name, src)
    for p in provs:
        if p in p2r and p2r[p] != rid:
            problems.append("province {} is in BOTH region {} ({}) and region {} ({})".format(
                p, p2r[p], r_src[p2r[p]][0], rid, name))
        p2r[p] = rid

print("states:", len(s2p), "| regions:", len(r2p))
print("duplicate state ids:", dupe_state_ids or "none")

# ---- 1. every land province in exactly one state ---------------------------
missing_state = sorted(land - set(p2s))
print("\n[1] land provinces in NO state :", len(missing_state), missing_state[:20])

# ---- 2. every province in exactly one strategic region ---------------------
missing_region = sorted(land - set(p2r))
print("[2] land provinces in NO region:", len(missing_region), missing_region[:20])

# ---- 3. a state must not straddle strategic regions ------------------------
print("\n[3] states whose provinces span MORE THAN ONE strategic region:")
straddle = []
for sid, provs in s2p.items():
    regs = {}
    for p in provs:
        r = p2r.get(p)
        regs.setdefault(r, []).append(p)
    if len(regs) > 1:
        straddle.append((sid, regs))
if not straddle:
    print("    none")
for sid, regs in sorted(straddle):
    name, src = s_src[sid]
    print("    state {:<5} {:<32} [{}]".format(sid, name, src))
    for r, ps in sorted(regs.items(), key=lambda kv: -len(kv[1])):
        rn = r_src.get(r, ("?", "?"))[0] if r is not None else "NONE"
        print("        region {:<6} {:<34} {:>4} provinces  {}".format(
            str(r), rn, len(ps), sorted(ps)[:10]))

# ---- 4. provinces listed in a state/region that do not exist ---------------
ghost_s = sorted(set(p2s) - allp)
ghost_r = sorted(set(p2r) - allp)
print("\n[4] non-existent provinces referenced by a state :", ghost_s[:20] or "none")
print("    non-existent provinces referenced by a region:", ghost_r[:20] or "none")

print("\n[5] duplicate-membership problems:", len(problems))
for p in problems[:20]:
    print("    ", p)


# ---------------------------------------------------------------- deeper checks

# province id -> terrain type, needed by the checks below
ptype = {}
with open(os.path.join(G, "map", "definition.csv"), encoding="utf-8-sig") as _f:
    for _row in csv.reader(_f, delimiter=";"):
        if len(_row) >= 5 and _row[0].isdigit():
            ptype[int(_row[0])] = _row[4]

bad_vp, bad_bld, bad_type, bad_other = [], [], [], []

for name, (path, src) in sorted(effective(r"history\states").items()):
    raw = open(path, encoding="utf-8-sig", errors="replace").read()
    t = re.sub(r"#[^\n]*", "", raw)

    sid = re.search(r"\bid\s*=\s*(\d+)", t)
    if not sid:
        continue
    sid = int(sid.group(1))
    pm = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
    provs = set(int(x) for x in pm.group(1).split()) if pm else set()

    # 1. victory_points must point at a province the state still owns
    for vp in re.finditer(r"victory_points\s*=\s*\{([^}]*)\}", t):
        nums = [int(x) for x in re.findall(r"\d+", vp.group(1))]
        # pairs of (province, value)
        for i in range(0, len(nums) - 1, 2):
            if nums[i] not in provs:
                bad_vp.append((sid, name, src, nums[i], nums[i + 1]))

    # 2. province-level buildings: buildings = { <pid> = { ... } }
    for bm in re.finditer(r"buildings\s*=\s*\{", t):
        start = bm.end()
        depth, i = 1, start
        while i < len(t) and depth:
            if t[i] == "{":
                depth += 1
            elif t[i] == "}":
                depth -= 1
            i += 1
        block = t[start:i - 1]
        for pm2 in re.finditer(r"(\d+)\s*=\s*\{", block):
            pid = int(pm2.group(1))
            if pid not in provs:
                bad_bld.append((sid, name, src, pid))

    # 3. provinces of the wrong terrain type inside a land state
    for p in provs:
        tt = ptype.get(p)
        if tt is None:
            bad_other.append((sid, name, src, p, "NOT IN definition.csv"))
        elif tt != "land":
            bad_type.append((sid, name, src, p, tt))


def show(title, rows, fmt):
    print("\n=== {} : {} ===".format(title, len(rows)))
    for r in rows[:25]:
        print("   ", fmt(r))
    if not rows:
        print("    none")


show("victory_points on a province the state does NOT contain", bad_vp,
     lambda r: "state {:<5} {:<32} [{}]  VP province {} (value {})".format(r[0], r[1], r[2], r[3], r[4]))
show("province-level buildings outside the state", bad_bld,
     lambda r: "state {:<5} {:<32} [{}]  province {}".format(r[0], r[1], r[2], r[3]))
# Lakes inside land states are NORMAL - vanilla does it in over a hundred
# states - so only the ones inside a file this mod overrides are worth seeing.
_mine = [r for r in bad_type if r[2] == "WiF"]
print("")
print("=== non-land provinces inside a state : {} total, {} in WiF files ===".format(
    len(bad_type), len(_mine)))
print("    (vanilla does this widely; only WiF-overridden files are listed)")
for r in _mine:
    print("     state {:<5} {:<32} province {} is '{}'".format(r[0], r[1], r[3], r[4]))
if not _mine:
    print("     none")

show("provinces missing from definition.csv", bad_other,
     lambda r: "state {:<5} {:<32} [{}]  province {} {}".format(r[0], r[1], r[2], r[3], r[4]))


# ---------------------------------------------------------------- verdict
_fatal = (len(dupe_state_ids) + len(problems) + len(straddle) + len(bad_vp)
          + len(bad_bld) + len(ghost_s) + len(ghost_r)
          + len([x for x in missing_state if x])
          + len([x for x in missing_region if x]))
print("")
print("=" * 62)
print("  FATAL-CLASS PROBLEMS: {}".format(_fatal))
if _fatal:
    print("  FIX THESE BEFORE LAUNCHING - they crash HOI4 during map init")
    print("  with nothing useful written to error.log.")
else:
    print("  Map data is consistent. Nothing here would crash the game.")
print("=" * 62)
