"""The generic post-SME warlord tree - a placeholder, about ten years long.

Layout, names, costs, prerequisites and exclusives come from the Focus Tree
Planner map "Post-SME Warlords (generic)" (doc map-etstw2m7), snapshotted in
tools/planner_post_sme_warlords.json. Re-snapshot that file after editing the
map, then re-run this. Rewards and icons live here, keyed by focus id.

Every focus is a SHARED focus, so one definition serves two trees:
  * wif_post_sme_warlord_tree - its own tree, for the nine breakaways of the
    SME collapse (loaded in wif_sme_form_<TAG>, tools/gen_sme_collapse.py).
  * wif_sme_unravelling_tree - the SME and ZWF keep their loss tree and get
    this one beside it (shared_focus line spliced into
    common/national_focus/wif_sme_unravelling.txt).
Game x = planner x + 2, which clears the Unravelling focuses at x 1-5.

Writes:
  common/national_focus/wif_post_sme_shared.txt   shared focuses
  common/national_focus/wif_post_sme_warlord.txt  the breakaways' tree
  common/national_focus/wif_sme_unravelling.txt   shared_focus line only
  common/ideas/wif_post_sme_ideas.txt
  common/scripted_effects/wif_post_sme_effects.txt
  localisation/english/wif_post_sme_l_english.yml
"""
import glob
import json
import math
import os
import re

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r'C:\Program Files (x86)\Steam\steamapps\common\Hearts of Iron IV'
X_SHIFT = 2
TREE = 'wif_post_sme_warlord_tree'
ROOT_FOCUS = 'wif_pws_root'
BREAKAWAYS = ['RUE', 'VGD', 'GRK', 'OSG', 'KMR', 'ARB', 'RNS', 'RFS', 'SPT']


def p(*a):
    return os.path.join(MOD, *a)


def write(rel, text, bom=False, nl='\r\n'):
    os.makedirs(os.path.dirname(p(rel)), exist_ok=True)
    data = text.replace('\r\n', '\n').replace('\n', nl).encode('utf-8')
    open(p(rel), 'wb').write((b'\xef\xbb\xbf' if bom else b'') + data)
    print('wrote', rel)


def cost(days):
    # Weeks, rounded UP to three decimals so the game's floor shows the right day.
    w = days / 7
    if abs(w - round(w)) < 1e-9:
        return str(int(round(w)))
    return f'{math.ceil(w * 1000) / 1000:.3f}'


# ---------------------------------------------------------------- rewards
# Building in the capital needs a free slot, so every factory comes with one.
def build(kind, n=1):
    return (f'capital_scope = {{\n\tadd_extra_state_shared_building_slots = {n}\n'
            f'\tadd_building_construction = {{ type = {kind} level = {n} instant_build = yes }}\n}}')


def cap(body):
    return 'capital_scope = {\n' + '\n'.join('\t' + l for l in body.split('\n')) + '\n}'


def stock(kind, n):
    return f'add_equipment_to_stockpile = {{ type = {kind} amount = {n} producer = ROOT }}'


INFRA2 = ('random_owned_controlled_state = {\n\tlimit = { infrastructure < 5 }\n'
          '\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }\n'
          '\tset_state_flag = wif_pws_branch_line\n}\n'
          'random_owned_controlled_state = {\n\tlimit = { infrastructure < 5 NOT = { has_state_flag = wif_pws_branch_line } }\n'
          '\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }\n}')

R = {
    'root': 'add_stability = 0.05',
    'count': 'add_political_power = 25',
    'garrison_rule': 'add_war_support = 0.05\nadd_stability = -0.05',
    'provisional_soviet': 'add_stability = 0.05\nadd_war_support = -0.05',
    'seal': 'add_political_power = 50',
    'feuds': 'add_stability = 0.05',
    'strongman': 'add_ideas = wif_pws_strongman_idea',
    'elections': 'add_ideas = wif_pws_town_soviets',
    'constitution': 'add_stability = 0.05',
    'recognition': ('add_political_power = 50\nevery_neighbor_country = {\n'
                    '\tadd_opinion_modifier = { target = ROOT modifier = wif_sme_old_comrades }\n}'),
    'neither': 'add_war_support = 0.05\nadd_stability = 0.05',
    'state': 'wif_pws_become_a_state = yes',
    'envoys': ('every_country = {\n\tlimit = { wif_is_russian_warlord = yes NOT = { tag = ROOT } }\n'
               '\tadd_opinion_modifier = { target = ROOT modifier = wif_sme_old_comrades }\n'
               '\tROOT = { add_opinion_modifier = { target = PREV modifier = wif_sme_old_comrades } }\n}'),
    'brothers': ('random_neighbor_country = {\n\tlimit = { wif_is_russian_warlord = yes NOT = { has_war_with = ROOT } }\n'
                 '\tdiplomatic_relation = { country = ROOT relation = non_aggression_pact active = yes }\n}'),
    'trust_no_one': ('add_war_support = 0.05\nrandom_neighbor_country = {\n\tlimit = { wif_is_russian_warlord = yes }\n'
                     '\trandom_owned_controlled_state = {\n\t\tlimit = { any_neighbor_state = { is_owned_by = ROOT } }\n'
                     '\t\tadd_claim_by = ROOT\n\t}\n}'),
    'trade': 'add_timed_idea = { idea = wif_pws_trade_idea days = 365 }',
    'fed': 'add_stability = 0.05',
    'cadre': 'army_experience = 25',
    'militia': 'add_manpower = 15000',
    'drill': 'add_ideas = wif_pws_drill_manuals',
    'junctions': cap('add_building_construction = {\n\ttype = bunker\n\tlevel = 1\n'
                     '\tprovince = { all_provinces = yes limit_to_victory_point = yes }\n\tinstant_build = yes\n}'),
    'few_trained': 'add_ideas = wif_pws_few_but_trained',
    'every_man': 'add_ideas = wif_pws_every_man_a_rifle',
    'artillery': stock('artillery_equipment', 100),
    'mortars': stock('support_equipment', 200),
    'lorries': stock('motorized_equipment', 100),
    'border': 'add_ideas = wif_pws_border_posts',
    'standing': 'set_country_flag = wif_pws_standing_army\nwif_recalculate_battalion_cap = yes',
    'inventory': 'add_tech_bonus = { name = wif_pws_inventory_bonus bonus = 0.5 uses = 1 category = industry }',
    'power': cap('add_building_construction = { type = infrastructure level = 1 instant_build = yes }'),
    'mines': cap('add_resource = { type = steel amount = 2 }'),
    'workshops': build('industrial_complex'),
    'timber': 'add_ideas = wif_pws_exports',
    'branch_lines': INFRA2,
    'rail_workshops': stock('train_equipment', 10),
    'small_arms': build('arms_factory'),
    'second_shift': build('industrial_complex') + '\nadd_stability = -0.02',
    'plan': 'add_ideas = wif_pws_five_year_plan',
    'tractors': build('industrial_complex'),
    'scrap': cap('add_resource = { type = steel amount = 4 }'),
    'own_economy': ('if = {\n\tlimit = { has_idea = wif_russian_warlord_economy }\n'
                    '\tadd_ideas = partial_economic_mobilisation\n}'),
    'choose_capital': cap('add_extra_state_shared_building_slots = 1'),
    'survey': 'add_political_power = 25',
    'housing': cap('add_manpower = 10000'),
    'rubble': cap('add_extra_state_shared_building_slots = 1'),
    'water': cap('add_manpower = 10000') + '\nadd_stability = 0.02',
    'electric': cap('add_extra_state_shared_building_slots = 1'),
    'hospital': cap('add_manpower = 10000'),
    'schools': 'add_ideas = wif_pws_institute',
    'trams': cap('add_building_construction = { type = infrastructure level = 1 instant_build = yes }'),
    'villages': cap('add_manpower = 25000\nadd_extra_state_shared_building_slots = 1'),
    'city': 'wif_pws_the_capital_rises = yes',
}

ICON = {
    'root': 'occupy_states_ongoing_war', 'count': 'allies_build_infantry',
    'garrison_rule': 'military_sphere', 'provisional_soviet': 'propaganda',
    'seal': 'national_unity', 'feuds': 'political_pressure', 'strongman': 'forceful_treaty',
    'elections': 'neutrality_focus', 'constitution': 'national_unity',
    'recognition': 'improve_relations', 'neither': 'neutrality_focus', 'state': 'national_unity',
    'envoys': 'improve_relations', 'brothers': 'alliance', 'trust_no_one': 'more_territorial_claims',
    'trade': 'trade', 'fed': 'consumer_goods', 'cadre': 'army_doctrines',
    'militia': 'axis_build_infantry', 'drill': 'army_doctrines', 'junctions': 'defence',
    'few_trained': 'special_forces', 'every_man': 'allies_build_infantry',
    'artillery': 'army_artillery', 'mortars': 'army_artillery2', 'lorries': 'army_motorized',
    'border': 'fortify_city', 'standing': 'position_armies',
    'inventory': 'production', 'power': 'construct_infrastructure', 'mines': 'oil_refinery',
    'workshops': 'construct_civ_factory', 'timber': 'positive_trade_relations',
    'branch_lines': 'construct_infrastructure', 'rail_workshops': 'construction2',
    'small_arms': 'small_arms', 'second_shift': 'construct_civilian', 'plan': 'production2',
    'tractors': 'construct_civ_factory', 'scrap': 'construct_military', 'own_economy': 'soviet_construction',
    'choose_capital': 'fortify_city', 'survey': 'construction', 'housing': 'construct_civilian',
    'rubble': 'construction2', 'water': 'construction', 'electric': 'secret_weapon',
    'hospital': 'consumer_goods', 'schools': 'scientific_exchange', 'trams': 'construct_infrastructure',
    'villages': 'soviet_construction', 'city': 'national_unity',
}

FILTER = {'political': 'FOCUS_FILTER_POLITICAL', 'inner': 'FOCUS_FILTER_STABILITY',
          'diplomacy': 'FOCUS_FILTER_POLITICAL', 'military': 'FOCUS_FILTER_ARMY_XP',
          'industry': 'FOCUS_FILTER_INDUSTRY', 'economy': 'FOCUS_FILTER_INDUSTRY'}

IDEAS = {
    'wif_pws_strongman_idea': ('generic_secret_police', {'political_power_factor': 0.1, 'war_support_factor': 0.05}),
    'wif_pws_town_soviets': ('generic_democratic_drift_bonus', {'political_power_gain': 0.05, 'stability_factor': 0.05}),
    'wif_pws_trade_idea': ('generic_flexible_foreign_policy', {'trade_opinion_factor': 0.5}),
    'wif_pws_drill_manuals': ('generic_army_war_college', {'training_time_army_factor': -0.05}),
    'wif_pws_few_but_trained': ('generic_infantry_bonus', {'army_org_factor': 0.05, 'conscription_factor': -0.05}),
    'wif_pws_every_man_a_rifle': ('generic_manpower_bonus', {'conscription': 0.01, 'army_org_factor': -0.05}),
    'wif_pws_border_posts': ('generic_fortify_the_borders', {'army_core_defence_factor': 0.05}),
    'wif_pws_exports': ('generic_production_bonus', {'local_resources_factor': 0.1}),
    'wif_pws_five_year_plan': ('generic_build_infrastructure', {'production_speed_buildings_factor': 0.05}),
    'wif_pws_institute': ('generic_research_bonus', {'research_speed_factor': 0.03}),
}
IDEA_NAME = {
    'wif_pws_strongman_idea': ("The Strongman's Peace", 'One man decides, and the arguments end.'),
    'wif_pws_town_soviets': ('Town Soviets', 'The towns choose their own councils - under supervision.'),
    'wif_pws_trade_idea': ('Trade Across the Lines', 'Grain for fuel, timber for rifles, with whoever is buying.'),
    'wif_pws_drill_manuals': ('Old Army Drill Manuals', "The Red Army's regulations, reprinted on whatever paper there is."),
    'wif_pws_few_but_trained': ('Few but Trained', 'A small army that can fight, rather than a large one that cannot.'),
    'wif_pws_every_man_a_rifle': ('Every Man a Rifle', 'No professional army - only the whole people, armed.'),
    'wif_pws_border_posts': ('Border Posts', 'Marked borders, guarded crossings, and fewer raids.'),
    'wif_pws_exports': ('Timber and Coal for Sale', 'The only things we have more of than we need.'),
    'wif_pws_five_year_plan': ('A Plan for Five Years', 'Modest targets, actually met.'),
    'wif_pws_institute': ('The Technical Institute', 'Engineers for the factories have to come from somewhere.'),
}

# State size classes, smallest first; The Capital Rises moves the capital up one.
CATEGORIES = ['wasteland', 'enclave', 'tiny_island', 'small_island', 'pastoral', 'rural',
              'town', 'large_town', 'city', 'large_city', 'metropolis', 'megalopolis']


def indent(s, n):
    return '\n'.join(('\t' * n + l) if l else l for l in s.split('\n'))


def load_map():
    m = json.load(open(p('tools', 'planner_post_sme_warlords.json'), encoding='utf-8'))
    by_id = {f['id']: f for f in m['focuses']}
    for f in m['focuses']:
        f['key'] = f['fid'].replace('wif_pws_', '')
        assert f['key'] in R, f'no reward for {f["fid"]}'
        assert f['key'] in ICON, f'no icon for {f["fid"]}'
    return m, by_id


def gen_shared(m, by_id):
    o = ['# GENERATED by tools/gen_post_sme_tree.py from the Focus Tree Planner',
         '# (tools/planner_post_sme_warlords.json) - do not edit by hand.',
         '#',
         '# The generic post-SME warlord tree, as shared focuses: included whole by',
         f'# {TREE} and by wif_sme_unravelling_tree through',
         f'# shared_focus = {ROOT_FOCUS}. Placeholder content, about ten years.',
         '']
    for f in sorted(m['focuses'], key=lambda f: (f['y'], f['x'])):
        o.append('shared_focus = {')
        o.append(f'\tid = {f["fid"]}')
        o.append(f'\ticon = GFX_goal_generic_{ICON[f["key"]]}')
        if f['pre']:
            ids = [by_id[i]['fid'] for i in f['pre']]
            if f['any']:
                o.append('\tprerequisite = { ' + ' '.join(f'focus = {i}' for i in ids) + ' }')
            else:
                for i in ids:
                    o.append(f'\tprerequisite = {{ focus = {i} }}')
        if f['mx']:
            o.append('\tmutually_exclusive = { ' + ' '.join(f'focus = {by_id[i]["fid"]}' for i in f['mx']) + ' }')
        o.append(f'\tx = {f["x"] + X_SHIFT}')
        o.append(f'\ty = {f["y"]}')
        o.append(f'\tcost = {cost(f["days"])}')
        o.append(f'\tsearch_filters = {{ {FILTER[f["branch"]]} }}')
        o.append(f'\tai_will_do = {{ factor = {5 if f["mx"] else 10} }}')
        o.append('\tcompletion_reward = {')
        o.append(indent(R[f['key']], 2))
        o.append('\t}')
        o.append('}')
        o.append('')
    write('common/national_focus/wif_post_sme_shared.txt', '\n'.join(o))


def continuous_y():
    # Below the lowest focus: the 770x380 continuous window covers the top-left otherwise.
    m = json.load(open(p('tools', 'planner_post_sme_warlords.json'), encoding='utf-8'))
    return (max(f['y'] for f in m['focuses']) + 2) * 130


def gen_tree():
    tags = '\n'.join(f'\t\t\t\ttag = {t}' for t in BREAKAWAYS)
    o = ['# GENERATED by tools/gen_post_sme_tree.py - do not edit by hand.',
         '#',
         '# The tree for the nine breakaways of the SME collapse. Loaded by',
         '# wif_sme_form_<TAG> (tools/gen_sme_collapse.py); the country block lets',
         '# the game pick it too. All focuses are in wif_post_sme_shared.txt.',
         '',
         'focus_tree = {',
         f'\tid = {TREE}',
         '',
         '\tcountry = {',
         '\t\tfactor = 0',
         '\t\tmodifier = {',
         '\t\t\tadd = 10',
         '\t\t\tOR = {',
         tags,
         '\t\t\t}',
         '\t\t}',
         '\t}',
         '',
         '\tdefault = no',
         f'\tcontinuous_focus_position = {{ x = 50 y = {continuous_y()} }}',
         '',
         f'\tshared_focus = {ROOT_FOCUS}',
         '}',
         '']
    write('common/national_focus/wif_post_sme_warlord.txt', '\n'.join(o))


def splice_unravelling():
    rel = 'common/national_focus/wif_sme_unravelling.txt'
    s = open(p(rel), 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in s else '\n'
    start, end = '\t# >>> GENERATED post-SME tree', '\t# <<< GENERATED post-SME tree'
    block = nl.join([start,
                     '\t# The generic warlord tree beside the loss tree (tools/gen_post_sme_tree.py).',
                     f'\tshared_focus = {ROOT_FOCUS}',
                     f'\tcontinuous_focus_position = {{ x = 50 y = {continuous_y()} }}',
                     end])
    if start in s:
        s = re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: block, s, flags=re.S)
    else:
        anchor = '\tdefault = no' + nl
        assert s.count(anchor) == 1, 'unravelling anchor'
        s = s.replace(anchor, anchor + nl + block + nl)
    open(p(rel), 'wb').write(s.encode('utf-8'))
    print('spliced', rel)


def gen_ideas():
    o = ['# GENERATED by tools/gen_post_sme_tree.py - do not edit by hand.', '',
         'ideas = {', '\tcountry = {']
    for k, (pic, mods) in IDEAS.items():
        o += [f'\t\t{k} = {{', f'\t\t\tpicture = {pic}', '\t\t\tallowed = { always = no }',
              '\t\t\tremoval_cost = -1', '\t\t\tmodifier = {']
        o += [f'\t\t\t\t{a} = {b}' for a, b in mods.items()]
        o += ['\t\t\t}', '\t\t}']
    o += ['\t}', '}', '']
    write('common/ideas/wif_post_sme_ideas.txt', '\n'.join(o))


def state_vps():
    """Highest victory point province of every state that was Soviet or is one
    of WiF's own, mod files over vanilla."""
    files = {}
    for d in (os.path.join(GAME, 'history', 'states'), p('history', 'states')):
        for f in glob.glob(os.path.join(d, '*.txt')):
            t = re.sub(r'#.*', '', open(f, encoding='utf-8-sig', errors='replace').read())
            mm = re.search(r'\bid\s*=\s*(\d+)', t)
            if mm:
                files[int(mm.group(1))] = t
    out = {}
    for sid, t in files.items():
        if not re.search(r'add_core_of\s*=\s*(SOV|SME)\b', t) and not 1082 <= sid <= 1085:
            continue
        vps = [(int(v), int(pr)) for pr, v in re.findall(r'victory_points\s*=\s*\{\s*(\d+)\s+(\d+)', t)]
        if vps:
            out[sid] = max(vps)[1]
    return out


def gen_effects():
    vps = state_vps()
    o = ['# GENERATED by tools/gen_post_sme_tree.py - do not edit by hand.', '',
         '# A State, Not a Warband: the broken warlord spirit gives way to the',
         '# ordinary one. Still a warlord, still weak.',
         'wif_pws_become_a_state = {',
         '\tif = {', '\t\tlimit = { has_idea = wif_russian_warlord_broken }',
         '\t\tremove_ideas = wif_russian_warlord_broken',
         '\t\tadd_ideas = wif_russian_warlord', '\t}',
         '\twif_recalculate_battalion_cap = yes', '}', '',
         '# The Capital Rises. Country scope.',
         '#   * the state goes up one size class',
         '#   * +1 civilian factory and +1 building slot',
         '#   * +5 victory points on its main victory point province (table of every',
         f'#     Soviet state, {len(vps)} of them; a capital outside it gets none)',
         '#   * if it is one of the towns urban on the map but disguised, the',
         '#     disguise comes off (wif_raise_capital_city, tools/gen_capital_cities.py)',
         'wif_pws_the_capital_rises = {',
         '\tcapital_scope = {']
    first = True
    for lo, hi in zip(CATEGORIES, CATEGORIES[1:]):
        o.append(f'\t\t{"if" if first else "else_if"} = {{ limit = {{ has_state_category = {lo} }} set_state_category = {hi} }}')
        first = False
    o += ['\t\tadd_extra_state_shared_building_slots = 2',
          '\t\tadd_building_construction = { type = industrial_complex level = 1 instant_build = yes }']
    first = True
    for sid, prov in sorted(vps.items()):
        o.append(f'\t\t{"if" if first else "else_if"} = {{ limit = {{ state = {sid} }} add_victory_points = {{ province = {prov} value = 5 }} }}')
        first = False
    o += ['\t}', '\twif_raise_capital_city = yes', '}', '']
    write('common/scripted_effects/wif_post_sme_effects.txt', '\n'.join(o))


def esc(s):
    return s.replace('\\n', '\n').replace('"', '\\"').replace('\n', '\\n')


def gen_loc(m):
    o = ['l_english:']
    for f in m['focuses']:
        flav = re.split(r'\n\nEffect:|\\n\\nEffect:', f['desc'])[0].strip()
        o.append(f' {f["fid"]}:0 "{esc(f["name"])}"')
        o.append(f' {f["fid"]}_desc:0 "{esc(flav)}"')
    for k, (n, d) in IDEA_NAME.items():
        o.append(f' {k}:0 "{esc(n)}"')
        o.append(f' {k}_desc:0 "{esc(d)}"')
    o.append(' wif_pws_inventory_bonus:0 "Inventory the Workshops"')
    write('localisation/english/wif_post_sme_l_english.yml', '\n'.join(o) + '\n', bom=True)


if __name__ == '__main__':
    m, by_id = load_map()
    gen_shared(m, by_id)
    gen_tree()
    splice_unravelling()
    gen_ideas()
    gen_effects()
    gen_loc(m)
