"""Balkan map changes: Banja Luka split from Bosnia, and Sarajevo and
Ljubljana as real cities.

    python tools/gen_balkan_map.py

1. BANJA LUKA (new state 1086), from Bosnia (104): provinces 9922 11572 6983
   6957 3985 9586, with Bosnia's second victory point (6983, Banja Luka).
   Yugoslav-owned, Yugoslav and Bosnian cores - so a released Bosnia takes it
   too (vanilla releases BOS by core). A quarter of Bosnia's population, half
   its aluminium (3 of 7), infrastructure 1. Croatia takes it when it breaks
   away (tools/gen_cro_ndh.py), and it is one of the three places Tito can put
   his headquarters.
   map/buildings.txt: the province-level spawns on the six provinces (bunker,
   supply_node, special_project_facility_spawn) follow their ground to 1086;
   every per-state slot of Bosnia's that stood on them is moved onto ground
   Bosnia keeps, copying the coordinates of a Bosnian supply node; 1086 gets
   the same set of per-state slots Bosnia has, at fresh points inside its own
   provinces (height = heightmap pixel / 10). No province crosses a strategic
   region. Run tools/check_map.py afterwards.
2. SARAJEVO (11899) AND LJUBLJANA (9627) become cities like Zagreb: urban
   terrain (tools/gen_capital_cities.py, PERMANENT), city ground painted into
   map/terrain.bmp (index 13, the urban texture the city meshes stand on) as a
   Zagreb-sized patch around the province's centre, and Bosnia raised to
   Zagreb's state category (large_town; Ljubljana already is).

Re-run after any HoI4 map patch: map/terrain.bmp is a full copy of vanilla's.
"""
import os, random, re, struct

import numpy as np

GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 5632, 2048

BOSNIA, BANJA_LUKA = 104, 1086
MOVING = [9922, 11572, 6983, 6957, 3985, 9586]
PROVINCE_LEVEL = {'bunker', 'supply_node', 'special_project_facility_spawn'}
BLOCKING = {'rocket_site_spawn', 'naval_base_spawn', 'naval_headquarters', 'naval_supply_hub'}
CITIES = {11899: 'Sarajevo', 9627: 'Ljubljana'}
URBAN_INDEX = 13
CITY_PIXELS = 64            # Zagreb (11581) has 64 urban pixels


def p(*a):
    return os.path.join(MOD, *a)


def province_map():
    colour = {}
    for l in open(os.path.join(GAME, 'map', 'definition.csv'), encoding='latin-1'):
        f = l.strip().split(';')
        if len(f) > 6 and f[0].isdigit():
            colour[(int(f[1]) << 16) | (int(f[2]) << 8) | int(f[3])] = int(f[0])
    b = open(os.path.join(GAME, 'map', 'provinces.bmp'), 'rb').read()
    off = struct.unpack('<I', b[10:14])[0]
    a = np.frombuffer(b, dtype=np.uint8, offset=off, count=W * H * 3).reshape(H, W, 3)
    key = (a[:, :, 2].astype(np.int64) << 16) | (a[:, :, 1].astype(np.int64) << 8) | a[:, :, 0]
    ids = np.zeros((H, W), dtype=np.int32)
    for k, pid in colour.items():
        ids[key == k] = pid
    return ids


def heights():
    h = open(os.path.join(GAME, 'map', 'heightmap.bmp'), 'rb').read()
    off = struct.unpack('<I', h[10:14])[0]
    return np.frombuffer(h, dtype=np.uint8, offset=off, count=W * H).reshape(H, W)


# ------------------------------------------------------------------ states
def states():
    src = open(os.path.join(GAME, 'history', 'states', '104-Bosnia.txt'), encoding='utf-8-sig').read()
    m = re.search(r'provinces=\{([^}]*)\}', src)
    provs = [int(x) for x in m.group(1).split()]
    assert set(MOVING) <= set(provs), 'a moving province is not in vanilla Bosnia'
    keep = [x for x in provs if x not in MOVING]
    t = src.replace(m.group(0), 'provinces={\n\t\t' + ' '.join(map(str, keep)) + ' \n\t}')
    t = re.sub(r'\t\tvictory_points = \{\n\t\t\t6983 3\n\t\t\}\n', '', t)
    assert '6983' not in t
    t = t.replace('manpower =1910200', 'manpower = 1432650 # 3/4 of vanilla 1910200 - Banja Luka (1086) has the rest')
    t = t.replace('aluminium=7 # was: 10', 'aluminium=4 # vanilla 7 - Banja Luka (1086) has 3')
    t = t.replace('state_category = town', 'state_category = large_town # Sarajevo is a city, as Zagreb (WiF)')
    assert 'large_town' in t and 'aluminium=4' in t and '1432650' in t
    hdr = '# Welt in Flammen (tools/gen_balkan_map.py): Banja Luka split off as state 1086; Sarajevo a city.\n'
    # NO BOM: a BOM in front of the leading comment breaks the parse of the
    # whole state file, and the game then crashes at map load (2026-11-20).
    open(p('history', 'states', '104-Bosnia.txt'), 'w', encoding='utf-8', newline='\n').write(hdr + t)
    open(p('history', 'states', '1086-Banja Luka.txt'), 'w', encoding='utf-8', newline='\n').write(f'''# Welt in Flammen (tools/gen_balkan_map.py): split from Bosnia (104).
state={{
	id={BANJA_LUKA}
	name="STATE_{BANJA_LUKA}" # Banja Luka
	manpower = 477550 # 1/4 of vanilla Bosnia

	state_category = rural

	resources={{
		aluminium=3 # half of vanilla Bosnia's 7
	}}

	history={{
		owner = YUG
		victory_points = {{
			6983 3
		}}
		buildings = {{
			infrastructure = 1
		}}
		add_core_of = YUG
		add_core_of = BOS
	}}

	provinces={{
		{' '.join(map(str, MOVING))}
	}}

	local_supplies=0.0
}}
''')
    print('wrote history/states/104-Bosnia.txt and 1086-Banja Luka.txt')


def loc():
    path = p('localisation', 'english', 'wif_states_l_english.yml')
    raw = open(path, 'rb').read()
    t = raw.decode('utf-8-sig')
    if f'STATE_{BANJA_LUKA}:' in t:
        print('state name already there')
        return
    nl = '\r\n' if '\r\n' in t else '\n'
    t = t.rstrip('\r\n') + nl + f' STATE_{BANJA_LUKA}:0 "Banja Luka"' + nl + ' VICTORY_POINTS_6983:0 "Banja Luka"' + nl
    open(path, 'wb').write(b'\xef\xbb\xbf' + t.encode('utf-8'))
    print('added the Banja Luka state name')


# ------------------------------------------------------------------ buildings.txt
def buildings(ids, hm):
    path = p('map', 'buildings.txt')
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8')
    nl = '\r\n' if '\r\n' in text else '\n'
    lines = text.split(nl)
    if any(l.startswith(f'{BANJA_LUKA};') for l in lines):
        print('map/buildings.txt already has Banja Luka - left alone')
        return
    moving = set(MOVING)

    def prov(l):
        f = l.split(';')
        return int(ids[int(float(f[4])), int(float(f[2]))])

    bosnia = [i for i, l in enumerate(lines) if l.startswith(f'{BOSNIA};')]
    anchors = [lines[i].split(';') for i in bosnia
               if lines[i].split(';')[1] == 'supply_node' and prov(lines[i]) not in moving]
    per_state = {}
    relocated = 0
    for i in bosnia:
        f = lines[i].split(';')
        kind = f[1]
        if kind in BLOCKING:
            assert prov(lines[i]) not in moving, f'{kind} on a moving province - cannot split here'
        per_state[kind] = per_state.get(kind, 0) + (kind not in PROVINCE_LEVEL)
        if prov(lines[i]) in moving:
            if kind in PROVINCE_LEVEL:
                f[0] = str(BANJA_LUKA)                       # follows its ground
            else:
                a = anchors[relocated % len(anchors)]        # stays Bosnian, moves within Bosnia
                f[2], f[3], f[4] = a[2], a[3], a[4]
                relocated += 1
            lines[i] = ';'.join(f)
    # Banja Luka's own per-state slots, at fresh points on its own ground
    pts = np.argwhere(np.isin(ids, MOVING))
    rng = random.Random(1086)
    new = []
    for kind, n in sorted(per_state.items()):
        for _ in range(n):
            y, x = pts[rng.randrange(len(pts))]
            new.append(f'{BANJA_LUKA};{kind};{x + 0.5:.2f};{hm[y, x] / 10:.2f};{y + 0.5:.2f};{rng.uniform(0, 6.28):.2f};0')
    last = max(bosnia)
    lines[last + 1:last + 1] = new
    open(path, 'wb').write(nl.join(lines).encode('utf-8'))
    print(f'map/buildings.txt: {relocated} Bosnian slots moved within Bosnia, {len(new)} new Banja Luka slots',
          {k: v for k, v in per_state.items() if v})


# ------------------------------------------------------------------ cities
def terrain(ids):
    src = open(os.path.join(GAME, 'map', 'terrain.bmp'), 'rb').read()
    off = struct.unpack('<I', src[10:14])[0]
    t = np.frombuffer(src, dtype=np.uint8, offset=off, count=W * H).reshape(H, W).copy()
    for pid, name in CITIES.items():
        pts = np.argwhere(ids == pid)
        cy, cx = pts.mean(axis=0)
        order = np.argsort((pts[:, 0] - cy) ** 2 + (pts[:, 1] - cx) ** 2)
        for y, x in pts[order[:CITY_PIXELS]]:
            t[y, x] = URBAN_INDEX
        print(f'{name}: {min(CITY_PIXELS, len(pts))} of {len(pts)} pixels painted urban')
    out = src[:off] + t.tobytes() + src[off + W * H:]
    open(p('map', 'terrain.bmp'), 'wb').write(out)
    print('wrote map/terrain.bmp')


def main():
    ids = province_map()
    states()
    loc()
    buildings(ids, heights())
    terrain(ids)


if __name__ == '__main__':
    main()
