"""The SME's war with the Ostschild and the breakup that follows a defeat.

Source of truth for the breakaway states. Writes:
  common/country_tags/wif_sme_collapse_countries.txt
  common/names/wif_sme_collapse_names_auto.txt        (vanilla SOV name pool per tag)
  common/countries/<name>.txt                       (one per breakaway)
  common/countries/colors.txt                       (appends missing tags)
  common/scripted_effects/zz_wif_sme_a0_tables_auto.txt
  common/scripted_effects/zz_wif_sme_b_breakaways_auto.txt
  common/scripted_localisation/wif_sme_war_bar.txt
  interface/wif_sme_war.gfx
  events/wif_sme_switch_auto.txt
  localisation/english/wif_sme_war_auto_l_english.yml

Hand-written alongside: zz_wif_sme_a_common.txt (helpers the breakaways
call), zz_wif_sme_c_war.txt (score, war, collapse driver, Zhukov split),
events/wif_sme_war.txt, common/ideas/wif_sme_war.txt, the slider GUI and the
Unravelling focus tree. Scripted effects load in file-name order, hence a/b/c.
Flags and portraits: tools/gen_sme_collapse_assets.py.
"""
import glob
import os
import re

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(*a):
    return os.path.join(MOD, *a)


# The order is the order they break away. `step` is the collapse step that
# forms them; step 4 is the Zhukov split (zz_wif_sme_c_war.txt).
#   army: share of what the losing government still has (each split takes its
#   fraction of what is LEFT, so "10%" is a tenth of the remainder each time).
BREAKAWAYS = [
    dict(tag='RUE', step=1, name='Russian Empire', adj='Russian', file='Russian Empire',
         states=[400], capital=400, party='neutrality', ideology='wif_absolute_monarchism',
         leader='Vladimir III Romanov', picture='GFX_portrait_SME_vladimir_iii',
         pops=dict(neutrality=70, communism=10, fascism=15, democratic=5),
         color=(238, 222, 150), color_ui=(250, 238, 175), army=0.1, monarchy=True, kirov=True),
    dict(tag='VGD', step=2, name='Neutral State of Vologda', adj='Vologdan', file='Neutral State of Vologda',
         states=[351], capital=351, party='neutrality', ideology='despotism',
         leader='Valimer Kasparov', picture='GFX_portrait_wif_kasparov',
         pops=dict(neutrality=75, communism=15, fascism=5, democratic=5),
         color=(206, 72, 62), color_ui=(232, 105, 95), army=0.1),
    dict(tag='GRK', step=3, name='Gorky Soviet Republic', adj='Gorky', file='Gorky Soviet Republic',
         states=[252], capital=252, party='communism', ideology='leninism',
         leader='Leyanold Raziv', picture='GFX_portrait_wif_raziv',
         pops=dict(communism=80, neutrality=10, fascism=5, democratic=5),
         color=(150, 28, 58), color_ui=(190, 60, 90), army=0.1),
    dict(tag='OSG', step=5, name='Orthodox Order of Saint George', adj='Georgian Order',
         file='Orthodox Order of Saint George',
         states=[1085], capital=1085, party='neutrality', ideology='wif_theocracy',
         leader='Cyril Pavlov', picture='GFX_portrait_wif_pavlov',
         pops=dict(neutrality=80, fascism=10, communism=5, democratic=5),
         color=(228, 178, 22), color_ui=(245, 205, 70), army=0, druzhina=True),
    dict(tag='KMR', step=6, name='Free Republic of Komi', adj='Komi', file='Free Republic of Komi',
         states=[397, 880, 262, 581], capital=397, party='democratic', ideology='socialism',
         leader='Nikolai Voznesensky', picture='GFX_portrait_wif_voznesensky',
         pops=dict(democratic=25, communism=25, fascism=25, neutrality=25),
         color=(58, 150, 108), color_ui=(95, 185, 140), army=0.1, elections=True),
    dict(tag='ARB', step=7, name='Aryan Brotherhood', adj='Brotherhood', file='Aryan Brotherhood',
         states=[398], capital=398, party='fascism', ideology='nazism',
         leader='Alexey Dobrovolsky', picture='GFX_portrait_wif_dobrovolsky',
         pops=dict(fascism=75, neutrality=15, communism=5, democratic=5),
         color=(62, 62, 66), color_ui=(110, 110, 116), army=0.1),
    dict(tag='RNS', step=8, name='Russian National State', adj='Russian', file='Russian National State',
         states=[1084, 1083, 1082, 399], capital=1084, party='democratic', ideology='conservatism',
         leader='Boris Yeltsin', picture='GFX_portrait_wif_yeltsin',
         pops=dict(democratic=60, neutrality=20, communism=10, fascism=10),
         color=(48, 82, 170), color_ui=(85, 120, 210), army=0.1, elections=True, hates='ARB'),
    dict(tag='RFS', step=9, name='Russian Fascist State', adj='Russian', file='Russian Fascist State',
         states=[251, 401], capital=251, party='fascism', ideology='fascism_ideology',
         leader='Yuri Molotov', picture='GFX_portrait_wif_molotov',
         pops=dict(fascism=75, neutrality=15, communism=5, democratic=5),
         color=(128, 104, 26), color_ui=(170, 145, 60), army=0.1),
    dict(tag='SPT', step=10, name='Syndicalist State of the True Proletariat', adj='Syndicalist',
         file='Syndicalist State of the True Proletariat',
         states=[652, 582, 651, 573], capital=652, party='communism', ideology='marxism',
         leader='Leonid Brezhnev', picture='GFX_portrait_wif_brezhnev',
         pops=dict(communism=80, neutrality=10, democratic=5, fascism=5),
         color=(222, 82, 34), color_ui=(245, 120, 70), army=0.1),
]

# The Zhukov split's second tag. Its own name is Zhukov's army; when it is the
# council's southern government instead, the cosmetic ZWF_EMERGENCY gives it
# the SME's name and flag.
ZWF = dict(tag='ZWF', name='West Russian Army Front', adj='Army Front', file='West Russian Army Front',
           color=(118, 16, 16), color_ui=(165, 45, 45))

# Points for taking a city (state id: points). Losing one the SME took costs
# double. Pre-war SME states are scored separately (-40, Gorky -55).
CITIES = {
    255: 5, 239: 5, 260: 5, 254: 5, 264: 5,          # Penza Saratov Voronezh Ryazan Tikhvin
    217: 10, 195: 10, 247: 10, 248: 10, 223: 10,     # Stalingrad Leningrad Kalinin Yaroslavl Tula
    219: 20,                                         # Moscow
    236: 5, 821: 5,                                  # Astrakhan Grozny
    229: 15, 231: 15,                                # Baku Tiflis
    234: 10,                                         # Krasnodar
    227: 15, 221: 15, 202: 15, 206: 15, 808: 15, 812: 15,  # Stalino Kharkov Kiev Minsk Riga Tallinn
    242: 15,                                         # Smolensk
}

SPRITES_PORTRAIT = ['kasparov', 'raziv', 'pavlov', 'voznesensky', 'dobrovolsky', 'yeltsin',
                    'molotov', 'brezhnev']

HEADER = '# GENERATED by tools/gen_sme_collapse.py - edit the generator, not this file.\n\n'


def write(path, text, bom=False, crlf=False):
    if crlf:
        text = text.replace('\r\n', '\n').replace('\n', '\r\n')
    with open(path, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='') as f:
        f.write(text)


def side_owns(states):
    ors = ' '.join(f'state = {s}' for s in states)
    return f'OR = {{ {ors} }} wif_sme_side_owns = yes'


def gen_breakaway(b):
    t = b['tag']
    o = []
    o.append(f'# {b["name"]}: {", ".join(str(s) for s in b["states"])}.')
    o.append(f'wif_sme_form_{t} = {{')
    o.append(f'\tif = {{')
    o.append(f'\t\tlimit = {{ any_state = {{ {side_owns(b["states"])} }} }}')
    o.append(f'\t\tevery_state = {{')
    o.append(f'\t\t\tlimit = {{ {side_owns(b["states"])} }}')
    o.append(f'\t\t\ttransfer_state_to = {t}')
    o.append(f'\t\t\tadd_core_of = {t}')
    o.append(f'\t\t\tremove_core_of = SME')
    o.append(f'\t\t\tremove_core_of = ZWF')
    o.append(f'\t\t}}')
    o.append(f'\t\t{t} = {{')
    o.append(f'\t\t\tif = {{')
    o.append(f'\t\t\t\tlimit = {{ owns_state = {b["capital"]} }}')
    o.append(f'\t\t\t\tset_capital = {{ state = {b["capital"]} }}')
    o.append(f'\t\t\t}}')
    # The generic warlord tree (tools/gen_post_sme_tree.py).
    o.append(f'\t\t\tload_focus_tree = {{ tree = wif_post_sme_warlord_tree keep_completed = no }}')
    o.append(f'\t\t\tinherit_technology = event_target:wif_sme_south')
    o.append(f'\t\t\tset_research_slots = 3')
    el = 'yes' if b.get('elections') else 'no'
    o.append(f'\t\t\tset_politics = {{ ruling_party = {b["party"]} elections_allowed = {el} }}')
    pops = ' '.join(f'{k} = {v}' for k, v in b['pops'].items())
    o.append(f'\t\t\tset_popularities = {{ {pops} }}')
    if b.get('monarchy'):
        o.append(f'\t\t\twif_become_absolute_monarchy = yes')
    o.append(f'\t\t\tcreate_country_leader = {{')
    o.append(f'\t\t\t\tname = "{b["leader"]}"')
    o.append(f'\t\t\t\tpicture = "{b["picture"]}"')
    o.append(f'\t\t\t\texpire = "1975.1.1"')
    o.append(f'\t\t\t\tideology = {b["ideology"]}')
    o.append(f'\t\t\t\ttraits = {{ }}')
    o.append(f'\t\t\t}}')
    if b.get('monarchy'):
        o.append(f'\t\t\twif_apply_subideology_modifiers = yes')
    o.append(f'\t\t\tset_stability = 0.35')
    o.append(f'\t\t\tset_war_support = 0.3')
    o.append(f'\t\t\twif_sme_ruin_country = yes')
    if b.get('hates'):
        h = b['hates']
        o.append(f'\t\t\tif = {{')
        o.append(f'\t\t\t\tlimit = {{ country_exists = {h} }}')
        o.append(f'\t\t\t\tadd_opinion_modifier = {{ target = {h} modifier = wif_sme_fierce_dislike }}')
        o.append(f'\t\t\t}}')
    o.append(f'\t\t}}')
    if b.get('kirov'):
        o.append(f'\t\twif_sme_kirov_becomes_vyatka = yes')
    if b.get('druzhina'):
        o.append(f'\t\twif_sme_druzhina_of_saint_george = yes')
    if b['army']:
        r = b['army']
        o.append(f'\t\tevent_target:wif_sme_south = {{')
        o.append(f'\t\t\ttransfer_units_fraction = {{')
        o.append(f'\t\t\t\ttarget = {t}')
        o.append(f'\t\t\t\tsize = 0')
        o.append(f'\t\t\t\tarmy_ratio = {r}')
        o.append(f'\t\t\t\tnavy_ratio = 0')
        o.append(f'\t\t\t\tair_ratio = {r}')
        o.append(f'\t\t\t\tstockpile_ratio = {r}')
        # Leaders stay home: transfer_units_fraction moves unit leaders with
        # their divisions, and once took Zhukov - the SME's own leader - to
        # the Russian Empire. Breakaways get generated generals instead.
        o.append(f'\t\t\t\tkeep_unit_leaders_trigger = {{ always = yes }}')
        o.append(f'\t\t\t}}')
        o.append(f'\t\t}}')
    o.append(f'\t\t# The player of the government it left may follow it.')
    o.append(f'\t\tevent_target:wif_sme_south = {{')
    o.append(f'\t\t\tif = {{')
    o.append(f'\t\t\t\tlimit = {{ is_ai = no }}')
    o.append(f'\t\t\t\tcountry_event = {{ id = wif_sme_switch.{b["step"]} }}')
    o.append(f'\t\t\t}}')
    o.append(f'\t\t}}')
    o.append(f'\t}}')
    o.append(f'}}')
    return '\n'.join(o)


def gen_effects():
    o = [HEADER.rstrip('\n')]
    o.append('# Breakaway states of the SME collapse. Called one a step by')
    o.append('# wif_sme_collapse_step (zz_wif_sme_c_war.txt). Each takes its states from')
    o.append('# the SME side only - whatever the Ostschild kept at the peace stays theirs -')
    o.append('# and does nothing at all if the SME side holds none of them.')
    o.append('')
    for b in BREAKAWAYS:
        o.append(gen_breakaway(b))
        o.append('')
    return '\n'.join(o) + '\n'


def gen_tables():
    o = [HEADER.rstrip('\n')]
    o.append('# Loaded before zz_wif_sme_a_common.txt, which calls these.')
    o.append('')
    # The city table, seeded when the war starts.
    o.append('# Global scope: the cities that score, and what they are worth.')
    o.append('wif_sme_seed_cities = {')
    for s, v in CITIES.items():
        o.append(f'\t{s} = {{ set_variable = {{ wif_sme_pts = {v} }} }}')
    o.append('}')
    o.append('')

    # Spirits to strip from the SME side at the collapse.
    names = set()
    for f in glob.glob(p('**', '*.txt'), recursive=True):
        if not re.search(r'(?i)sme|sov|white_question|siber|far_east', os.path.basename(f)):
            continue
        t = open(f, encoding='utf-8', errors='ignore').read()
        for m in re.finditer(r'add_ideas\s*=\s*(\{[^}]*\}|\S+)', t):
            names.update(re.findall(r'[A-Za-z_]\w*', m.group(1)))
    names = sorted(n for n in names if n.startswith('wif_') and not n.startswith('wif_russian_warlord'))
    o.append('# Country scope: every national spirit the SME can hold, except the warlord')
    o.append('# spirit and its law. Collected from the SME, SOV and Siberian files.')
    o.append('wif_sme_strip_spirits = {')
    for n in names:
        o.append(f'\tif = {{ limit = {{ has_idea = {n} }} remove_ideas = {n} }}')
    o.append('}')
    return '\n'.join(o) + '\n'


def gen_switch_events():
    o = [HEADER + 'add_namespace = wif_sme_switch\n']
    o.append('# One per breakaway: the SME-side player may follow the new state.\n')
    for b in BREAKAWAYS:
        t, n = b['tag'], b['step']
        o.append(f'''country_event = {{
	id = wif_sme_switch.{n}
	title = wif_sme_switch.{n}.t
	desc = wif_sme_switch.{n}.d
	picture = GFX_report_event_soviet_soldiers

	is_triggered_only = yes

	option = {{
		name = wif_sme_switch.stay
		ai_chance = {{ factor = 100 }}
	}}
	option = {{
		name = wif_sme_switch.{n}.b
		trigger = {{ country_exists = {t} }}
		ai_chance = {{ factor = 0 }}
		{t} = {{ change_tag_from = ROOT }}
	}}
}}
''')
    return '\n'.join(o)


def gen_countries():
    tags = [HEADER.replace('\n\n', '\n')]
    for b in BREAKAWAYS + [ZWF]:
        tags.append(f'{b["tag"]} = "countries/{b["file"]}.txt"')
        write(p('common', 'countries', b['file'] + '.txt'),
              'graphical_culture = eastern_european_gfx\ngraphical_culture_2d = eastern_european_2d\n\n'
              '# Colours live in common/countries/colors.txt (tools/gen_sme_collapse.py).\n')
    write(p('common', 'country_tags', 'wif_sme_collapse_countries.txt'), '\n'.join(tags) + '\n')

    cpath = p('common', 'countries', 'colors.txt')
    text = open(cpath, encoding='utf-8', newline='').read()
    add = ''
    for b in BREAKAWAYS + [ZWF]:
        if re.search(rf'^{b["tag"]}\s*=', text, re.M):
            continue
        c, u = b['color'], b['color_ui']
        add += (f'{b["tag"]} = {{\r\n\tcolor = rgb {{ {c[0]} {c[1]} {c[2]} }}\r\n'
                f'\tcolor_ui = rgb {{ {u[0]} {u[1]} {u[2]} }}\r\n}}\r\n')
    if add:
        if not text.endswith('\n'):
            text += '\r\n'
        with open(cpath, 'w', encoding='utf-8', newline='') as f:
            f.write(text + add)


def gen_gfx():
    o = ['# GENERATED by tools/gen_sme_collapse.py.', '# Leaders of the SME breakaways (156x210, _small 67x67) and the war slider.', '',
         'spriteTypes = {']
    for n in SPRITES_PORTRAIT:
        o.append(f'\tspriteType = {{\n\t\tname = "GFX_portrait_wif_{n}"\n\t\ttexturefile = "gfx/leaders/SME/Portrait_wif_{n}.png"\n\t}}')
        o.append(f'\tspriteType = {{\n\t\tname = "GFX_portrait_wif_{n}_small"\n\t\ttexturefile = "gfx/leaders/SME/Portrait_wif_{n}_small.png"\n\t}}')
    for i in range(55):
        o.append(f'\tspriteType = {{\n\t\tname = "GFX_wif_sme_war_bar_{i:02d}"\n\t\ttexturefile = "gfx/interface/wif_sme_war/bar_{i:02d}.png"\n\t}}')
    o.append('}')
    write(p('interface', 'wif_sme_war.gfx'), '\n'.join(o) + '\n')

    # Scripted localisation: the slider frame for the current score.
    o = [HEADER.rstrip('\n'), 'defined_text = {', '\tname = wif_sme_war_bar_sprite']
    for i in range(55):
        score = -100 + i * 5
        if i < 54:
            trig = f'check_variable = {{ global.wif_sme_score < {score + 2.5} }}'
        else:
            trig = 'always = yes'
        o.append(f'\ttext = {{\n\t\ttrigger = {{ {trig} }}\n\t\tlocalization_key = GFX_wif_sme_war_bar_{i:02d}\n\t}}')
    o.append('}')
    write(p('common', 'scripted_localisation', 'wif_sme_war_bar.txt'), '\n'.join(o) + '\n')


def gen_loc():
    o = ['l_english:']
    for b in BREAKAWAYS + [ZWF]:
        t = b['tag']
        o.append(f' {t}:0 "{b["name"]}"')
        o.append(f' {t}_DEF:0 "the {b["name"]}"')
        o.append(f' {t}_ADJ:0 "{b["adj"]}"')
        for ide in ('communism', 'democratic', 'fascism', 'neutrality'):
            o.append(f' {t}_{ide}:0 "{b["name"]}"')
            o.append(f' {t}_{ide}_DEF:0 "the {b["name"]}"')
    for i in range(55):
        o.append(f' GFX_wif_sme_war_bar_{i:02d}:0 "GFX_wif_sme_war_bar_{i:02d}"')
    o.append(' wif_sme_switch.stay:0 "We stay with what is left."')
    for b in BREAKAWAYS:
        n, nm = b['step'], b['name']
        where = ', '.join(f'[{s}.GetName]' for s in b['states'])
        o.append(f' wif_sme_switch.{n}.t:0 "The {nm} Breaks Away"')
        o.append(f' wif_sme_switch.{n}.d:0 "{where} no longer answer to us. {b["leader"]} has '
                 f'declared the {nm}, and a part of the army has gone with him. Nobody is coming '
                 f'to stop it: there is nothing left to send."')
        o.append(f' wif_sme_switch.{n}.b:0 "Lead the {nm} instead."')
    write(p('localisation', 'english', 'wif_sme_war_auto_l_english.yml'), '\n'.join(o) + '\n', bom=True)


VANILLA_NAMES = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV\common\names\00_names.txt'


def gen_names():
    """Vanilla's SOV name pool for every breakaway, as SME and CRA already have
    in common/names/wif_names.txt. Without a pool, every character the game
    generates for them (advisors, replacement generals, operatives) logs
    'Failed to generate a name' and comes out as the engine placeholder."""
    src = open(VANILLA_NAMES, encoding='utf-8-sig').read().replace('\r\n', '\n')
    m = re.search(r'^SOV = \{\n(.*?)^\}', src, re.M | re.S)
    assert m, 'SOV name pool not found in vanilla 00_names.txt'
    body = m.group(1)
    out = [HEADER.rstrip('\n'),
           '# Vanilla SOV name pool, copied for each breakaway of the SME collapse.', '']
    for b in BREAKAWAYS + [ZWF]:
        out.append(f'{b["tag"]} = {{\n{body}}}\n')
    write(p('common', 'names', 'wif_sme_collapse_names_auto.txt'), '\n'.join(out), crlf=True)


def main():
    gen_countries()
    gen_names()
    write(p('common', 'scripted_effects', 'zz_wif_sme_a0_tables_auto.txt'), gen_tables())
    write(p('common', 'scripted_effects', 'zz_wif_sme_b_breakaways_auto.txt'), gen_effects())
    write(p('events', 'wif_sme_switch_auto.txt'), gen_switch_events())
    gen_gfx()
    gen_loc()
    print('ok')


if __name__ == '__main__':
    main()
