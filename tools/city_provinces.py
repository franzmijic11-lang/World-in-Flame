import os, re, glob

V = r"D:\Steam\steamapps\common\Hearts of Iron IV"
M = r"C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen"
OUT = os.path.join(M, "common", "scripted_effects", "wif_city_provinces.txt")

urban = set()
for line in open(os.path.join(V, "map", "definition.csv"), encoding="latin-1"):
    f = line.strip().split(";")
    if len(f) >= 7 and f[6] == "urban":
        urban.add(int(f[0]))

def parse(path):
    t = re.sub(r"#.*", "", open(path, encoding="utf-8-sig", errors="replace").read())
    m = re.search(r"\bid\s*=\s*(\d+)", t)
    if not m: return None
    pm = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
    return int(m.group(1)), [int(x) for x in pm.group(1).split()] if pm else []

states = {}
for p in glob.glob(os.path.join(V, "history", "states", "*.txt")):
    r = parse(p)
    if r: states[r[0]] = r[1]
modded = set()
for p in glob.glob(os.path.join(M, "history", "states", "*.txt")):
    r = parse(p)
    if r:
        states[r[0]] = r[1]
        modded.add(r[0])

counts = {s: sum(1 for x in pr if x in urban) for s, pr in states.items()}
live = {s: n for s, n in counts.items() if n > 0}

L = []
L.append("# GENERATED FILE - do not edit by hand.")
L.append("# Regenerate with tools/city_provinces.py after any change to state province")
L.append("# lists or to the map.")
L.append("#")
L.append("# HoI4 script has no province scope. There is no province iterator and")
L.append("# has_terrain is COUNTRY scope only (\"has any province of this terrain\"), so")
L.append("# \"how many city provinces are in this state\" cannot be asked at runtime. It is")
L.append("# therefore measured off the map here and baked into a state variable.")
L.append("#")
L.append("# A CITY PROVINCE IS A PROVINCE WITH urban TERRAIN in map/definition.csv -")
L.append("# the ones that draw as built-up ground. There are %d of them on the map." % len(urban))
L.append("# State membership comes from history/states, with this mod's %d overriding" % len(modded))
L.append("# files applied on top of vanilla's, so the province moves this mod makes are")
L.append("# reflected here.")
L.append("#")
L.append("# Only states with at least one are listed. An unset variable reads as 0 in")
L.append("# HoI4, so every state omitted here correctly counts as having no city.")
L.append("#")
L.append("# %d states have a city province: %d with one, %d with two, %d with three." % (
    len(live),
    sum(1 for n in live.values() if n == 1),
    sum(1 for n in live.values() if n == 2),
    sum(1 for n in live.values() if n == 3)))
L.append("#")
L.append("# Run once from on_startup, guarded by a global flag - province membership")
L.append("# cannot change during a game, so this never needs repeating.")
L.append("wif_seed_city_provinces = {")
for s in sorted(live):
    L.append("\t%d = { set_variable = { wif_city_provs = %d } }" % (s, live[s]))
L.append("}")

open(OUT, "wb").write(("\n".join(L) + "\n").encode("utf-8"))
print("wrote", OUT)
print("states seeded:", len(live), "| BOM:", open(OUT, "rb").read(3) == b"\xef\xbb\xbf")
