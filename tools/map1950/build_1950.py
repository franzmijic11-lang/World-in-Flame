"""Build the 1950 Axis-victory ownership for the WiF 1950 map page.
Writes states.json (one record per state) and countries.json."""
import json, os, re, sys, glob
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = r'C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen'
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
sys.path.insert(0, os.path.join(MOD, 'tools'))
import gen_jap_america_out_of_asia as AOOA
import gen_jap_china_peace as JCP
import gen_ita_pax_romana as PAX

M = json.load(open(os.path.join(HERE, 'map_src.json'), encoding='utf-8'))
S = {s['id']: s for s in M['states']}
own = {s['id']: s['owner'] for s in M['states']}
orig = dict(own)
note = {}   # state -> why it changed


def give(states, tag, why, only_from=None):
    for s in states:
        if s in own and (only_from is None or orig[s] in only_from or own[s] in only_from):
            if own[s] != tag:
                own[s] = tag
                note[s] = why


def of(*tags):
    return [s for s, o in orig.items() if o in tags]


# ---------------------------------------------------------------- Europe before the peace
give(of('AUS'), 'GER', 'Anschluss')
give([9, 75], 'RKH', 'Reichsprotektorat Böhmen und Mähren')
give([70, 71], 'SLO', 'Slovak State (German protectorate)')
give([664, 73], 'HUN', 'Vienna Awards')
give([69, 72, 74, 972], 'GER', 'Sudetenland and Silesia annexed')
give([10, 88, 90, 92, 89, 91], 'GEN', 'Generalgouvernement')
RKO = [11, 12, 13, 94, 95, 96, 189, 190, 191, 194, 204, 206, 784, 808, 809, 810, 811, 812, 813, 814, 815]
RKU = [93, 137, 193, 196, 197, 199, 200, 201, 202, 203, 221, 225, 226, 227, 228, 259]
RKM = [195, 205, 207, 208, 209, 210, 214, 217, 218, 219, 220, 222, 223, 224, 239, 240, 241, 242, 243, 244, 245, 246,
       247, 248, 250, 252, 253, 254, 255, 257, 258, 260, 263, 264, 265, 351, 879, 880]
RKK = [229, 230, 231, 232, 233, 234, 235, 236, 237, 238, 821, 826, 827, 828]
give(RKO, 'RKO', 'Reichskommissariat Ostland')
give(RKU, 'RKU', 'Reichskommissariat Ukraine')
give([s for s in of('POL') if own[s] == 'POL'], 'GER', 'Annexed into the Reich')

# ---------------------------------------------------------------- the Anglo-American peace (wif_peace_deal_map.txt)
t = open(os.path.join(MOD, 'common', 'scripted_effects', 'wif_peace_deal_map.txt'), encoding='utf-8').read()
first = {}
for m in re.finditer(r'(\d+) = \{ transfer_state_to = (\w+) \}', t):
    s = int(m.group(1))
    first.setdefault(s, m.group(2))   # the first branch is the "Italy fought / puppet exists" one
first[103] = 'ITA'                     # Croatia cedes Dalmatia at the final peace
for s, tag in first.items():
    give([s], tag, 'The Anglo-German peace')
give([144, 912], 'GER', 'The Anglo-German peace')
give([s for s in of('NOR') if own[s] == 'NOR'], 'RKG', 'Reichskommissariat Norwegen')
give([7, 35, 36], 'RKN', 'Reichskommissariat Niederlande')
give([6, 34, 977, 980], 'RKB', 'Reichskommissariat Belgien-Nordfrankreich')
give([s for s in of('LUX', 'BEL', 'HOL') if own[s] in ('LUX', 'BEL', 'HOL') and S[s]['lp'][0] > 1300 and S[s]['lp'][0] < 1500 and S[s]['lp'][1] < 300],
     'GER', 'The Anglo-German peace')
give([s for s in of('ALB')], 'ITA', 'Albania')
give(PAX.LIBYA, 'ITA', 'Italian Libya')
give(PAX.AOI_STATES + of('ETH'), 'AOI', 'Italian East Africa')
give([s for s in of('YUG') if own[s] == 'YUG'], 'SER', 'Serbia (German occupation)')
# France: Vichy has annexed what is left of France and its empire
give([s for s in of('FRA') if own[s] == 'FRA'], 'VIC', 'Vichy France annexes France')
# Britain: what is outside Europe and Africa goes to Canada (unless the peace or Japan took it)
for s in of('ENG'):
    if own[s] == 'ENG':
        x, y = S[s]['lp']
        europe_africa = (1250 <= x <= 1800 and y <= 700) or (1250 <= x <= 1900 and y <= 1024 and x <= 1800)
        if not europe_africa:
            give([s], 'CAN', 'British overseas territory to Canada')
give([s for s in of('LAT', 'LIT', 'EST') if own[s] in ('LAT', 'LIT', 'EST')], 'RKO', 'Reichskommissariat Ostland')

# ---------------------------------------------------------------- the Soviet surrender (events/wif_sov_events.txt)
give(RKM, 'RKM', 'Reichskommissariat Moskowien', only_from=['SOV'])
give(RKK, 'RKK', 'Reichskommissariat Kaukasien', only_from=['SOV'])
give([213, 215, 216] + [s for s in of('SOV') if S[s]['name'] in ('Karjala', 'Viipuri')], 'FIN', 'Greater Finland', only_from=['SOV'])
give([192, 834, 198, 829], 'GER', 'Annexed into the Reich', only_from=['SOV'])
give([408], 'JAP', 'Vladivostok to the owner of Korea')
give([404, 405, 585], 'CRA', 'Central Asian Red Army', only_from=['SOV'])
give([402, 406, 407, 583, 586, 587, 588, 589, 590, 881, 882], 'KAZ', 'Kazakhstan', only_from=['SOV'])
give([823, 830, 831], 'UZB', 'Uzbekistan', only_from=['SOV'])
give([584, 832, 1007], 'TMS', 'Turkmenistan')
give([732], 'KYR', 'Kyrgyzstan', only_from=['SOV'])
give([742, 1005], 'TAJ', 'Tajikistan')
# Siberia: the planner's own CSR / FES / WSM borders, and the Siberian Anarchy in the far north
for s in M['states']:
    if s.get('sib'):
        give([s['id']], s['owner'], 'The Siberian split')
give([516, 579, 644, 822, 824, 875, 876, 877, 878], 'SBA', 'Siberian Anarchy', only_from=['SOV'])
give([s for s in of('SOV') if own[s] == 'SOV'], 'SME', 'Soviet Military Emergency Government')

# ---------------------------------------------------------------- by 1950: Moskowien's civil war and the Siberian collapse
# The Novgorod rising (wif_nsr_revolt.txt): the SME annexes the eastern marches at once, and
# takes Archangelsk once it beats the Archangelsk emergency government (SME_archangelsk_is_ours).
# Moskowien wins its civil war, so the other risings and loyalist governments fold back in.
give([252, 879, 880], 'SME', "The SME annexes Moskowien's eastern marches in its civil war")
give([214], 'SME', 'The SME takes Archangelsk from its emergency government')
give([351], 'SME', 'The SME takes Vologda in the Moskowien civil war')
# Siberia has collapsed (gen_siberia_collapse.py), as painted in the Siberian Collapse Planner.
SIBC = {'wsm': 'WSM', 'csr': 'CSR', 'fes': 'FES', 'f9h25jf': 'NWA', 'foj20vy': 'SSB', 'fjv8uzk': 'YKT',
        'fjayd40': 'ANS', 'fnapr7o': 'SMG', 'fhse0cd': 'CLI', 'fnkp0hb': 'ICA'}
_plan = json.load(open(os.path.join(HERE, 'sibdb', 'plans', 'collapse.json'), encoding='utf-8'))
SIBC_COLOR = {}
for f in _plan['factions']:
    SIBC_COLOR[SIBC[f['id']]] = f['color']
for sid, fid in _plan['assign'].items():
    if fid in SIBC and SIBC[fid] not in ('WSM', 'CSR', 'FES'):
        give([int(sid)], SIBC[fid], 'The Siberian collapse')

# ---------------------------------------------------------------- Asia: China (gen_jap_china_peace.py) and the Pacific (America out of Asia)
give(list(JCP.TO_JAP), 'JAP', "Japan's dictated peace in China")
give(list(JCP.TO_RNG), 'RNG', "Japan's dictated peace in China")
give(list(JCP.NWA_STATES), 'CHI', 'The Northwestern Army retreats to Gansu')
give(list(JCP.TREATY_PORTS), 'JAP', 'Treaty ports seized')
give([s for s in of('SND', 'HBC')], 'JAP', 'Annexed by Japan')
give([s for s in of('GXC')], 'JAP', "Japan's dictated peace in China")
give(list(AOOA.JAP_STATES), 'JAP', 'America out of Asia')
give([AOOA.HAWAII], 'HAW', 'Hawaiian protectorate')
give(list(AOOA.GEA_STATES) + [AOOA.CHRISTMAS], 'GEA', 'Greater East Asian South East Asia')
give(list(AOOA.IFS_STATES), 'IFS', 'Indian Free State')
give([s for s in of('HOL') if own[s] == 'HOL' and S[s]['lp'][0] > 2000], 'GEA', 'Greater East Asian South East Asia')
give([s for s in of('PHI')], 'JAP', 'America out of Asia')

# ---------------------------------------------------------------- names, colours, overlords, trees
loc = {}
for root in (GAME, MOD):
    for fn in glob.glob(os.path.join(root, 'localisation', 'english', '*.yml')):
        for l in open(fn, encoding='utf-8-sig', errors='ignore'):
            mm = re.match(r'\s+([A-Z][A-Z0-9]{2}):\d*\s*"(.*)"', l)
            if mm:
                loc[mm.group(1)] = mm.group(2)
col = {}
for fn in [os.path.join(GAME, 'common', 'countries', 'colors.txt'), os.path.join(MOD, 'common', 'countries', 'colors.txt')]:
    if os.path.exists(fn):
        txt = open(fn, encoding='utf-8-sig', errors='ignore').read()
        for mm in re.finditer(r'\b([A-Z][A-Z0-9]{2})\s*=\s*\{\s*color\s*=\s*(rgb|RGB|hsv|HSV)?\s*\{\s*([\d.]+)\s+([\d.]+)\s+([\d.]+)\s*\}', txt):
            if (mm.group(2) or 'rgb').lower() == 'rgb':
                col[mm.group(1)] = '#%02x%02x%02x' % tuple(int(float(v)) for v in mm.group(3, 4, 5))
for tag, v in M['owners'].items():
    col.setdefault(tag, v['color'])
COLOR_FIX = {'GER': '#5d574c', 'RKO': '#8b8478', 'RKU': '#a39270', 'RKM': '#7a6d63', 'RKK': '#94806b', 'RKG': '#7c8794',
             'RKN': '#8c917c', 'RKB': '#9b8b80', 'RKH': '#8e8090', 'GEN': '#a8998a', 'RKF': '#b49e7a', 'RKZ': '#a58c6e',
             'RKR': '#8f7a5f', 'VIC': '#5577b0', 'SER': '#9a6e6e', 'SLO': '#6f7fa0'}
col.update(COLOR_FIX)
col.update({k: v for k, v in SIBC_COLOR.items() if k not in ('WSM', 'CSR', 'FES')})

NAMES = {
    'GER': 'Greater German Reich', 'ENG': 'Reichsprotektorat England', 'VIC': 'French State (Vichy)',
    'CHI': 'Northwestern Army Group', 'RNG': 'Reorganized National Government', 'PRC': "People's Republic of China (Yan'an)",
    'SME': 'Soviet Military Emergency Government', 'RKM': 'Reichskommissariat Moskowien', 'RKO': 'Reichskommissariat Ostland',
    'RKU': 'Reichskommissariat Ukraine', 'RKK': 'Reichskommissariat Kaukasien', 'RKG': 'Reichskommissariat Norwegen',
    'RKN': 'Reichskommissariat Niederlande', 'RKB': 'Reichskommissariat Belgien-Nordfrankreich', 'RKH': 'Protectorate of Bohemia and Moravia',
    'GEN': 'Generalgouvernement', 'RKF': 'Reichskommissariat Ostafrika', 'RKZ': 'Reichskommissariat Zentralafrika', 'RKR': 'Reichskommissariat Rhodesien',
    'JAP': 'Empire of Japan', 'GEA': 'Greater East Asian South East Asia', 'IFS': 'Indian Free State', 'HAW': 'Hawaii',
    'CSR': "Central Siberian Republic (Popov's remnant)", 'FES': "Far Eastern Union (Stalin's remnant)", 'WSM': "West Siberian Marxist Republic (Yagoda's remnant)",
    'SBA': 'Siberian Anarchy', 'CRA': 'Central Asian Red Army', 'CAN': 'Dominion of Canada (Imperial seat)', 'ITA': 'Kingdom of Italy (Pax Romana)',
    'NWA': 'New White Army', 'SSB': 'State of Siberia', 'YKT': 'Yakutsk', 'ANS': 'Anarchist State of Siberia',
    'SMG': 'Siberian Military Government', 'CLI': 'Chelyabinsk Institute', 'ICA': 'Imperial Cult of Alexei',
    'AOI': 'Italian East Africa', 'CRO': 'Independent State of Croatia', 'SER': 'Serbia', 'SLO': 'Slovak State', 'SCO': 'Scotland',
}
OVERLORD = {t: 'GER' for t in ['RKM', 'RKO', 'RKU', 'RKK', 'RKG', 'RKN', 'RKB', 'RKH', 'GEN', 'RKF', 'RKZ', 'RKR', 'ENG', 'VIC', 'DEN', 'SER', 'SLO']}
OVERLORD.update({t: 'JAP' for t in ['RNG', 'MAN', 'MEN', 'GEA', 'IFS', 'HAW']})
OVERLORD.update({t: 'ITA' for t in ['AOI', 'CRO', 'GRE', 'PAL', 'JOR', 'LEB', 'SYR']})
# Countries that get a WiF post-war focus tree (by 1950)
TREES = {
    'GER': 'The victorious Reich and the road to civil war (wif_ger_victory)', 'RKM': 'Reichskommissariat Moskowien',
    'SME': 'The SME tree, 1944-1952', 'ENG': 'Reichsprotektorat England', 'VIC': 'The Vichy rework', 'CAN': 'Canada after Britain falls',
    'ITA': 'Pax Romana', 'CRO': 'Axis Croatia (NDH)', 'USA': 'The American tree and state-by-state elections', 'JAP': 'Hinode no Teikoku',
    'RNG': 'The hollow economy and the three resistances', 'PRC': "Yan'an after the defeat", 'CHI': 'The Northwestern Army Group',
    'CSR': "Popov's Siberian republic", 'FES': "Stalin's Far East", 'WSM': "Yagoda's Urals",
}

states = []
for s in M['states']:
    states.append({'id': s['id'], 'n': s['name'], 'p': s['path'], 'lp': s['lp'], 'o36': orig[s['id']], 'o': own[s['id']],
                   'c': s.get('cells', 0), 'why': note.get(s['id'], '')})
used = Counter(own.values())
countries = {}
for tag, n in used.items():
    countries[tag] = {'name': NAMES.get(tag) or loc.get(tag) or tag, 'color': col.get(tag, '#9a9a9a'), 'states': n,
                      'overlord': OVERLORD.get(tag, ''), 'tree': TREES.get(tag, '')}
missing = [t for t in TREES if t not in used]
print('tree tags with no land:', missing)
print('states', len(states), 'countries', len(countries))
print(Counter(own.values()).most_common(30))
with open(os.path.join(HERE, 'states.json'), 'w', encoding='utf-8') as f:
    f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False, separators=(',', ':')) for r in states) + '\n]\n')
json.dump({'w': M['w'], 'h': M['h'], 'water': M['water'], 'countries': countries}, open(os.path.join(HERE, 'world.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, separators=(',', ':'))
