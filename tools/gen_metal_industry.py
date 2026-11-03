"""Metal industry: the Improved Metal Working Plants tech line and its buildings.

Source of truth for the whole feature. Rerun after editing anything here, or
after painting over an icon mold:
    python tools/gen_metal_industry.py

Tech line (UTTNH Industry tab, a stand-alone column right of Fuel Refining):
    1942  Improved Metal Working Plants      steel + aluminium manufacturers, +1 each
    1945  Improved Metal Working Plants II   steel/aluminium buildings +1 (now 2)
    1948  Chromium Working I | Plants III | Tungsten Working I
    1952  Chromium Working II               Tungsten Working II
    1955  Chromium Working III              Tungsten Working III
Plants III takes steel/aluminium to 3. Chromium/Tungsten I unlock their building
(+1), II and III raise it to 2 and 3.

Buildings: 30,000 IC, any free factory slot (shared slots), no per-type limit
beyond the slots themselves.

AI: builds a manufacturer only when that resource is in deficit even after its
trade deals (so it could not import enough from anyone willing to sell), or
when it does import that resource and its imports of all resources tie up more
than 40% of its civilian factories. Otherwise a negative weight holds the
engine's own refinery logic back from building them.

ICON MOLDS live in tools/icon_molds/. Paint over them (keep the size), rerun
this script, and the game textures are rebuilt:
    building_<metal>.png   46x46  construction / state view icon
    tech_<family>.png      64x64  tech tree icon (shared by I, II and III)
A mold that does not exist yet is created as a tinted vanilla placeholder; an
existing mold is never overwritten.

Writes:
    common/buildings/wif_metal_industry.txt
    common/technologies/wif_metal_industry.txt
    common/scripted_triggers/wif_metal_industry_triggers.txt
    common/ai_strategy/wif_metal_industry.txt
    localisation/english/wif_metal_industry_l_english.yml
    interface/wif_metal_industry.gfx
    interface/countrystateview.gfx        (vanilla copy, building strip widened)
    interface/countrytechtreeview.gui     (UTTNH 3.0 copy, one grid box added)
    gfx/interface/buildings/wif_building_icon_strip.dds
    gfx/interface/technologies/wif_*.dds

The two interface copies override by filename, so WiF must load after UTTNH;
descriptor.mod declares UTTNH 3.0 as a dependency for that. If UTTNH or vanilla
change those files, rerun this script to re-copy and re-patch them.
"""
import os
import re
from PIL import Image

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
UTTNH = r'C:\Program Files (x86)\Steam\steamapps\workshop\content\394360\3413890094'
MOLDS = os.path.join(MOD, 'tools', 'icon_molds')

COST = 30000
STATE_MAX = 25          # 50 Building Slots' civilian factory cap; slots are the real limit
FIRST_FRAME = 32        # vanilla building strip has 31 frames
TRADE_SHARE = 0.4       # imports may use at most this share of civilian factories
CIC = 8                 # resources bought per civilian factory (vanilla cic = 0.125)
RESOURCES = ['oil', 'aluminium', 'rubber', 'tungsten', 'steel', 'chromium', 'coal']

# building id, resource, unlocking tech, display name, placeholder tint
BUILDINGS = [
    ('wif_steel_manufacturer', 'steel', 'wif_metal_working_plants', 'Steel Manufacturer', (150, 165, 185)),
    ('wif_aluminium_manufacturer', 'aluminium', 'wif_metal_working_plants', 'Aluminium Manufacturer', (225, 230, 240)),
    ('wif_chromium_manufacturer', 'chromium', 'wif_chromium_working', 'Chromium Manufacturer', (110, 200, 175)),
    ('wif_tungsten_manufacturer', 'tungsten', 'wif_tungsten_working', 'Tungsten Manufacturer', (205, 145, 80)),
]
BLD = {b[0]: b for b in BUILDINGS}

# tech id, name, year, grid x, grid y, cost, family, enables, upgrades, leads to
# grid: x 0/2/4 = chromium/metal/tungsten; y follows UTTNH's industry rows
# (6 = 1941, 8 = 1943, 10 = 1945, 12 = 1948, 14 = 1952, 16 = 1955).
TECHS = [
    ('wif_metal_working_plants', 'Improved Metal Working Plants', 1942, 2, 7, 2.0, 'metal',
     ['wif_steel_manufacturer', 'wif_aluminium_manufacturer'], [],
     ['wif_metal_working_plants2']),
    ('wif_metal_working_plants2', 'Improved Metal Working Plants II', 1945, 2, 10, 2.0, 'metal',
     [], ['wif_steel_manufacturer', 'wif_aluminium_manufacturer'],
     ['wif_metal_working_plants3', 'wif_chromium_working', 'wif_tungsten_working']),
    ('wif_metal_working_plants3', 'Improved Metal Working Plants III', 1948, 2, 12, 2.5, 'metal',
     [], ['wif_steel_manufacturer', 'wif_aluminium_manufacturer'], []),
    ('wif_chromium_working', 'Chromium Working I', 1948, 0, 12, 2.5, 'chromium',
     ['wif_chromium_manufacturer'], [], ['wif_chromium_working2']),
    ('wif_chromium_working2', 'Chromium Working II', 1952, 0, 14, 2.5, 'chromium',
     [], ['wif_chromium_manufacturer'], ['wif_chromium_working3']),
    ('wif_chromium_working3', 'Chromium Working III', 1955, 0, 16, 3.0, 'chromium',
     [], ['wif_chromium_manufacturer'], []),
    ('wif_tungsten_working', 'Tungsten Working I', 1948, 4, 12, 2.5, 'tungsten',
     ['wif_tungsten_manufacturer'], [], ['wif_tungsten_working2']),
    ('wif_tungsten_working2', 'Tungsten Working II', 1952, 4, 14, 2.5, 'tungsten',
     [], ['wif_tungsten_manufacturer'], ['wif_tungsten_working3']),
    ('wif_tungsten_working3', 'Tungsten Working III', 1955, 4, 16, 3.0, 'tungsten',
     [], ['wif_tungsten_manufacturer'], []),
]
FAMILY_TINT = {'metal': (160, 175, 195), 'chromium': (110, 200, 175), 'tungsten': (205, 145, 80)}
ROOT = TECHS[0][0]
GRID_X, GRID_Y = 1600, 172    # fuel_silos_tree is at 1250; Fuel Refining sits at 1460
FILLER_WIDTH = 2000           # UTTNH's industry tab is 1550 wide

TECH_DESC = {
    'wif_metal_working_plants': "Purpose-built rolling mills and electrolytic smelters let us turn imported ore and scrap into steel and aluminium at home, rather than depending on what foreign markets will sell us.",
    'wif_metal_working_plants2': "Continuous casting and better furnace linings raise the output of every steel and aluminium manufacturer we operate.",
    'wif_metal_working_plants3': "Oxygen converters and modern reduction cells push our steel and aluminium plants to their full capacity.",
    'wif_chromium_working': "Recovering chromium from low-grade ore and alloy scrap lets us build plants dedicated to this vital alloying metal.",
    'wif_chromium_working2': "Improved leaching and reduction processes raise the yield of our chromium manufacturers.",
    'wif_chromium_working3': "Fully modernised chromium works extract every last trace of the metal from their feedstock.",
    'wif_tungsten_working': "Tungsten recovery from scheelite tailings and worn tooling makes dedicated tungsten plants worthwhile.",
    'wif_tungsten_working2': "Better powder metallurgy raises the output of our tungsten manufacturers.",
    'wif_tungsten_working3': "Modern carbide recycling and refining bring our tungsten manufacturers to peak output.",
}


def write(rel, text, bom=False):
    path = os.path.join(MOD, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = text.replace('\r\n', '\n').replace('\n', '\r\n').encode('utf-8')
    if bom:
        data = b'\xef\xbb\xbf' + data
    with open(path, 'wb') as f:
        f.write(data)
    print('wrote', rel)


def tech_of(building):
    return BLD[building][2]


# ---------------------------------------------------------------- buildings
def gen_buildings():
    out = ['# Generated by tools/gen_metal_industry.py - edit that, not this.', 'buildings = {']
    for i, (bid, res, _tech, _name, _tint) in enumerate(BUILDINGS):
        out += [
            f'\t{bid} = {{',
            f'\t\tbase_cost = {COST}',
            f'\t\ticon_frame = {FIRST_FRAME + i}',
            f'\t\tlocal_resources_{res} = 1',
            '\t\trefinery = yes',
            '\t\tvalue = 3',
            '\t\tinfrastructure_construction_effect = yes',
            '\t\tlevel_cap = {',
            '\t\t\tshares_slots = yes',
            f'\t\t\tstate_max = {STATE_MAX}',
            '\t\t}',
            '\t}',
            '',
        ]
    out.append('}')
    write('common/buildings/wif_metal_industry.txt', '\n'.join(out) + '\n')


# ---------------------------------------------------------------- techs
def res_of_tech(t):
    bids = t[7] or t[8]
    return [BLD[b][1] for b in bids]


def gen_techs():
    out = ['# Generated by tools/gen_metal_industry.py - edit that, not this.',
           '# Stand-alone column in the UTTNH Industry tab; the grid box',
           f'# "{ROOT}_tree" is added to interface/countrytechtreeview.gui.',
           'technologies = {']
    for (tid, _name, year, x, y, cost, _fam, enables, upgrades, leads) in TECHS:
        t = (tid, _name, year, x, y, cost, _fam, enables, upgrades, leads)
        out.append(f'\t{tid} = {{')
        for b in enables:
            out += ['\t\tenable_building = {', f'\t\t\tbuilding = {b}', f'\t\t\tlevel = {STATE_MAX}', '\t\t}']
        if upgrades:
            out.append('\t\ton_research_complete = {')
            for b in upgrades:
                out += ['\t\t\tmodify_building_resources = {', f'\t\t\t\tbuilding = {b}',
                        f'\t\t\t\tresource = {BLD[b][1]}', '\t\t\t\tamount = 1', '\t\t\t}']
            out.append('\t\t}')
        for l in leads:
            out += ['\t\tpath = {', f'\t\t\tleads_to_tech = {l}', '\t\t\tresearch_cost_coeff = 1', '\t\t}']
        out += [
            f'\t\tresearch_cost = {cost}',
            f'\t\tstart_year = {year}',
            '\t\tfolder = {',
            '\t\t\tname = industry_folder',
            f'\t\t\tposition = {{ x = {x} y = {y} }}',
            '\t\t}',
            '\t\tcategories = {',
            '\t\t\tindustry',
            '\t\t}',
            '\t\tai_will_do = {',
            '\t\t\tfactor = 1',
        ]
        for res in res_of_tech(t):
            out += ['\t\t\tmodifier = {', '\t\t\t\tfactor = 3',
                    f'\t\t\t\thas_resources_in_country = {{ resource = {res} amount < 0 }}', '\t\t\t}',
                    '\t\t\tmodifier = {', '\t\t\t\tfactor = 2',
                    f'\t\t\t\thas_resources_in_country = {{ resource = {res} amount > 0 only_imported = yes }}',
                    '\t\t\t}']
            if upgrades:
                # upgrades are worth more to a country that already runs the plants
                out += ['\t\t\tmodifier = {', '\t\t\t\tfactor = 3',
                        f'\t\t\t\thas_resources_in_country = {{ resource = {res} amount > 0 buildings = yes }}',
                        '\t\t\t}']
        out += ['\t\t\tmodifier = {', '\t\t\t\tfactor = 2', '\t\t\t\twif_metal_trade_burden_high = yes', '\t\t\t}',
                '\t\t}', '\t}', '']
    out.append('}')
    write('common/technologies/wif_metal_industry.txt', '\n'.join(out) + '\n')


# ---------------------------------------------------------------- triggers + AI
def gen_triggers():
    out = ['# Generated by tools/gen_metal_industry.py - edit that, not this.', '',
           f'# Imports of all resources tie up more than {int(TRADE_SHARE * 100)}% of our civilian factories.',
           f'# A civilian factory buys {CIC} units of any resource (vanilla cic = {1 / CIC}).',
           'wif_metal_trade_burden_high = {',
           f'\tset_temp_variable = {{ wif_imp_cost = resource_imported@{RESOURCES[0]} }}']
    for r in RESOURCES[1:]:
        out.append(f'\tadd_to_temp_variable = {{ wif_imp_cost = resource_imported@{r} }}')
    out += [f'\tdivide_temp_variable = {{ wif_imp_cost = {CIC} }}',
            '\tset_temp_variable = { wif_imp_limit = num_of_civilian_factories }',
            f'\tmultiply_temp_variable = {{ wif_imp_limit = {TRADE_SHARE} }}',
            '\tcheck_variable = { wif_imp_cost > wif_imp_limit }',
            '}', '']
    for bid, res, tech, _n, _t in BUILDINGS:
        out += [f'# The AI should build a {res} plant: short even after trading, or',
                '# importing it while imports already cost too much.',
                f'wif_ai_wants_{bid} = {{',
                f'\thas_tech = {tech}',
                '\tOR = {',
                f'\t\thas_resources_in_country = {{ resource = {res} amount < 0 }}',
                '\t\tAND = {',
                f'\t\t\thas_resources_in_country = {{ resource = {res} amount > 0 only_imported = yes }}',
                '\t\t\twif_metal_trade_burden_high = yes',
                '\t\t}',
                '\t}',
                '}', '']
    write('common/scripted_triggers/wif_metal_industry_triggers.txt', '\n'.join(out))


def gen_ai():
    out = ['# Generated by tools/gen_metal_industry.py - edit that, not this.',
           '#',
           '# The manufacturers are refinery = yes buildings, which the engine\'s own',
           '# AI builds when short of a resource regardless of trade. These strategies',
           '# replace that with WiF\'s rule: import first, build only when imports',
           '# cannot cover the need or already cost more than 40% of civilian industry.',
           '# build_building values are weights in the AI\'s pick of what to build next;',
           '# the engine adds its own at weight 1, so the hold strategy cancels those.',
           '# A build strategy is skipped while that building is already under',
           '# construction, so the AI adds plants one at a time and re-checks.', '']
    for bid, res, tech, _n, _t in BUILDINGS:
        out += [f'wif_ai_build_{bid} = {{',
                '\tenable = {', f'\t\twif_ai_wants_{bid} = yes', '\t}',
                '\tabort_when_not_enabled = yes',
                '\tai_strategy = {', '\t\ttype = build_building', f'\t\tid = {bid}', '\t\tvalue = 20', '\t}',
                '}', '',
                f'# A deep {res} shortage gets a stronger push on top.',
                f'wif_ai_build_{bid}_urgent = {{',
                '\tenable = {', f'\t\twif_ai_wants_{bid} = yes',
                f'\t\thas_resources_in_country = {{ resource = {res} amount < -10 }}', '\t}',
                '\tabort_when_not_enabled = yes',
                '\tai_strategy = {', '\t\ttype = build_building', f'\t\tid = {bid}', '\t\tvalue = 30', '\t}',
                '}', '',
                f'wif_ai_hold_{bid} = {{',
                '\tenable = {', f'\t\thas_tech = {tech}', f'\t\tNOT = {{ wif_ai_wants_{bid} = yes }}', '\t}',
                '\tabort_when_not_enabled = yes',
                '\tai_strategy = {', '\t\ttype = build_building', f'\t\tid = {bid}', '\t\tvalue = -100', '\t}',
                '}', '']
    write('common/ai_strategy/wif_metal_industry.txt', '\n'.join(out))


# ---------------------------------------------------------------- localisation
def gen_loc():
    out = ['l_english:']
    for bid, res, _t, name, _tint in BUILDINGS:
        plural = name + 's'
        out += [f' {bid}: "{name}"',
                f' {bid}_plural: "{plural}"',
                f' {bid}_desc: "A dedicated works producing §Y{res.capitalize()}§! for the state it stands in. Takes a free factory slot, like a civilian factory. Output rises with research."']
    for t in TECHS:
        out += [f' {t[0]}: "{t[1]}"', f' {t[0]}_desc: "{TECH_DESC[t[0]]}"']
    write('localisation/english/wif_metal_industry_l_english.yml', '\n'.join(out) + '\n', bom=True)


# ---------------------------------------------------------------- icons
def tint(im, rgb):
    im = im.convert('RGBA')
    r, g, b, a = im.split()
    grey = Image.merge('RGB', (r, g, b)).convert('L')
    col = Image.merge('RGB', [grey.point(lambda v, c=c: v * c // 255) for c in rgb])
    col.putalpha(a)
    return col


def ensure_molds():
    os.makedirs(MOLDS, exist_ok=True)
    strip = Image.open(os.path.join(GAME, 'gfx', 'interface', 'buildings', 'building_icon_strip.dds')).convert('RGBA')
    fw = strip.width // 31
    refinery = strip.crop((9 * fw, 0, 10 * fw, strip.height))     # frame 10 = synthetic refinery
    for bid, res, _t, _n, rgb in BUILDINGS:
        p = os.path.join(MOLDS, f'building_{res}.png')
        if not os.path.exists(p):
            tint(refinery, rgb).save(p)
            print('created mold', os.path.relpath(p, MOD))
    readme = os.path.join(MOLDS, 'README.txt')
    with open(readme, 'w', encoding='utf-8', newline='\r\n') as f:
        f.write('Icon molds for the metal industry (tools/gen_metal_industry.py).\n\n'
                'Paint over these PNGs, keep the size and the transparent corners,\n'
                'then run:  python tools/gen_metal_industry.py\n\n'
                'building_<metal>.png  46x46  construction menu and state view icon,\n'
                '                             and also the tech tree icon:\n'
                '                             steel -> Metal Working Plants I-III,\n'
                '                             chromium/tungsten -> their Working I-III.\n'
                'tech_<family>.png     64x64  OPTIONAL: drop one in (family = metal,\n'
                '                             chromium or tungsten) to give that tech\n'
                '                             line its own art instead.\n\n'
                'Deleting a building mold makes the script recreate a tinted placeholder.\n')
    return strip, fw


# which building's art a tech line uses when no tech_<family>.png exists
TECH_ART = {'metal': 'steel', 'chromium': 'chromium', 'tungsten': 'tungsten'}


def tech_icon(fam):
    p = os.path.join(MOLDS, f'tech_{fam}.png')
    if os.path.exists(p):
        m = Image.open(p).convert('RGBA')
        if m.size != (64, 64):
            print(f'  note: tech_{fam}.png is {m.size}, resized to (64, 64)')
            m = m.resize((64, 64), Image.LANCZOS)
        return m
    art = Image.open(os.path.join(MOLDS, f'building_{TECH_ART[fam]}.png')).convert('RGBA')
    canvas = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
    big = art.resize((60, 60), Image.LANCZOS)
    canvas.paste(big, (2, 2), big)
    return canvas


def gen_icons():
    strip, fw = ensure_molds()
    h = strip.height
    wide = Image.new('RGBA', (fw * (31 + len(BUILDINGS)), h), (0, 0, 0, 0))
    wide.paste(strip.crop((0, 0, fw * 31, h)), (0, 0))
    for i, (bid, res, _t, _n, _rgb) in enumerate(BUILDINGS):
        m = Image.open(os.path.join(MOLDS, f'building_{res}.png')).convert('RGBA')
        if m.size != (fw, h):
            print(f'  note: building_{res}.png is {m.size}, resized to {(fw, h)}')
            m = m.resize((fw, h), Image.LANCZOS)
        wide.paste(m, (fw * (31 + i), 0))
    out = os.path.join(MOD, 'gfx', 'interface', 'buildings', 'wif_building_icon_strip.dds')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    wide.save(out)
    print('wrote', os.path.relpath(out, MOD))
    tdir = os.path.join(MOD, 'gfx', 'interface', 'technologies')
    os.makedirs(tdir, exist_ok=True)
    for fam in FAMILY_TINT:
        tech_icon(fam).save(os.path.join(tdir, f'wif_{fam}_working.dds'))
        print('wrote', f'gfx/interface/technologies/wif_{fam}_working.dds')
    out = ['# Generated by tools/gen_metal_industry.py - edit that, not this.', 'spriteTypes = {']
    for t in TECHS:
        out += ['\tspriteType = {', f'\t\tname = "GFX_{t[0]}_medium"',
                f'\t\ttexturefile = "gfx/interface/technologies/wif_{t[6]}_working.dds"', '\t}']
    out.append('}')
    write('interface/wif_metal_industry.gfx', '\n'.join(out) + '\n')
    return 31 + len(BUILDINGS)


# ---------------------------------------------------------------- interface overrides
def read_bytes_text(path):
    with open(path, 'rb') as f:
        raw = f.read()
    bom = raw.startswith(b'\xef\xbb\xbf')
    text = raw[3:].decode('utf-8') if bom else raw.decode('utf-8')
    return text, bom


def gen_statview(frames):
    text, bom = read_bytes_text(os.path.join(GAME, 'interface', 'countrystateview.gfx'))
    pat = re.compile(r'(name = "GFX_buildings_strip"\s*\r?\n\s*textureFile = )"[^"]*"(\s*\r?\n\s*noOfFrames = )\d+')
    new, n = pat.subn(r'\1"gfx/interface/buildings/wif_building_icon_strip.dds"\g<2>' + str(frames), text)
    assert n == 1, 'GFX_buildings_strip not found in vanilla countrystateview.gfx'
    nl = '\r\n' if '\r\n' in text else '\n'
    header = ('# WiF: vanilla copy with GFX_buildings_strip pointing at WiF\'s wider strip' + nl +
              '# (metal manufacturers). Generated by tools/gen_metal_industry.py.' + nl)
    with open(os.path.join(MOD, 'interface', 'countrystateview.gfx'), 'wb') as f:
        f.write((b'\xef\xbb\xbf' if bom else b'') + (header + new).encode('utf-8'))
    print('wrote interface/countrystateview.gfx')


def gen_techview():
    text, bom = read_bytes_text(os.path.join(UTTNH, 'interface', 'countrytechtreeview.gui'))
    nl = '\r\n' if '\r\n' in text else '\n'
    old = 'width = 1550 height = 1000'
    assert text.count(old) == 1, 'industry size_filler not found - UTTNH changed its tech screen'
    text = text.replace(old, f'width = {FILLER_WIDTH} height = 1000')
    anchor = re.search(r'\t\t\tgridboxtype = \{\s*name = "fuel_silos_tree".*?\n\t\t\t\}', text, re.S)
    assert anchor, 'fuel_silos_tree not found - UTTNH changed its tech screen'
    box = nl.join(['', '',
                   '\t\t\t# WiF metal industry (tools/gen_metal_industry.py)',
                   '\t\t\tgridboxtype = {',
                   f'\t\t\t\tname = "{ROOT}_tree"',
                   f'\t\t\t\tposition = {{ x = {GRID_X} y = {GRID_Y} }}',
                   '\t\t\t\tsize = { width = 350 height = 1200 }',
                   '\t\t\t\tslotsize = { width = 70 height = 70 }',
                   '\t\t\t\tformat = "UP"',
                   '\t\t\t}'])
    text = text[:anchor.end()] + box + text[anchor.end():]
    with open(os.path.join(MOD, 'interface', 'countrytechtreeview.gui'), 'wb') as f:
        f.write((b'\xef\xbb\xbf' if bom else b'') + text.encode('utf-8'))
    print('wrote interface/countrytechtreeview.gui')


if __name__ == '__main__':
    gen_buildings()
    gen_techs()
    gen_triggers()
    gen_ai()
    gen_loc()
    frames = gen_icons()
    gen_statview(frames)
    gen_techview()
