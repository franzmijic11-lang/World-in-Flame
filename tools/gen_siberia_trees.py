"""The three Siberian trees: Popov (CSR), Stalin (FES) and Yagoda (WSM).

Layout, names, costs, prerequisites, exclusives and which focuses "do
themselves" come from the Focus Tree Planner maps csr-popov-siberia,
fes-stalin-irkutsk and wsm-yagoda-urals, snapshotted in tools/planner_csr.json,
planner_fes.json and planner_wsm.json. Re-snapshot after editing a map, then
re-run this. Rewards and icons live here, keyed by focus id.

Self-completing focuses (dashed in the planner): the player can never pick
them - `available` waits on a flag that only the weekly timer sets. Once their
prerequisites are done the timer counts the planner's days in a variable
(wif_sib_t_<focus>) and then completes them. Weekly from on_weekly_<TAG>.

The negative spirits are tiered (_1 weakest .. _3 worst) and moved with
wif_sib_<spirit>_grow / _ease / _max / _remove. Nothing in Popov's tree can
reduce the anarchists or the Church, and nothing in Stalin's the Whites.

The war focuses (CSR March East, FES Hang the Traitor Popov) declare war and
set the global flag wif_siberian_war; WSM's Absolute Order sets the country
flag wif_wsm_absolute_order. The collapse mechanics that follow are the
user's, still to be written.

Writes:
  common/national_focus/wif_csr_focus.txt, wif_fes_focus.txt, wif_wsm_focus.txt
  common/ideas/wif_siberia_ideas.txt
  common/scripted_effects/wif_siberia_effects.txt
  common/on_actions/wif_siberia_on_actions.txt
  localisation/english/wif_siberia_l_english.yml
and splices the setup call into the three formation effects
(wif_central_siberia.txt, wif_far_east.txt, wif_west_siberia.txt).
"""
import json
import math
import os
import re

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(*a):
    return os.path.join(MOD, *a)


def write(rel, text, bom=False, nl='\r\n'):
    os.makedirs(os.path.dirname(p(rel)), exist_ok=True)
    data = text.replace('\r\n', '\n').replace('\n', nl).encode('utf-8')
    open(p(rel), 'wb').write((b'\xef\xbb\xbf' if bom else b'') + data)
    print('wrote', rel)


def cost(days):
    w = days / 7
    if abs(w - round(w)) < 1e-9:
        return str(int(round(w)))
    return f'{math.ceil(w * 1000) / 1000:.3f}'


def indent(s, n):
    return '\n'.join(('\t' * n + l) if l else l for l in s.split('\n'))


# ------------------------------------------------------------ spirits
# name: (picture, [modifiers per tier], loc name, loc desc)
# A single-tier spirit has one entry.
SPIRITS = {
    'anarchists': ('generic_communism_drift_bonus', [
        {'stability_factor': -0.05, 'industrial_capacity_factory': -0.03},
        {'stability_factor': -0.10, 'industrial_capacity_factory': -0.06},
        {'stability_factor': -0.15, 'industrial_capacity_factory': -0.10, 'production_speed_buildings_factor': -0.10},
    ], 'Anarchist Rebels', 'Black Banner bands hold the taiga villages and blow up the railway when it suits them. The republic has neither the men nor the authority to stop them.'),
    'church': ('generic_morale_bonus', [
        {'political_power_gain': -0.05, 'democratic_drift': -0.02},
        {'political_power_gain': -0.10, 'democratic_drift': -0.03},
        {'political_power_gain': -0.15, 'democratic_drift': -0.05},
    ], 'Heavy Church Influence', 'With the commissars gone, the Church came back faster than anyone expected, and it tells the villages that a parliament is godless.'),
    'food': ('generic_economic_crisis', [
        {'stability_factor': -0.03, 'consumer_goods_factor': 0.03},
        {'stability_factor': -0.06, 'consumer_goods_factor': 0.06},
        {'stability_factor': -0.10, 'consumer_goods_factor': 0.10, 'war_support_factor': -0.05},
    ], 'Food Shortages', 'Siberia never fed itself. The grain came from the west, and the west is gone.'),
    'soldiers_republic': ('generic_communist_army', [
        {'political_power_gain': -0.05},
        {'political_power_gain': -0.10, 'stability_factor': -0.05},
    ], 'A Republic of Soldiers', 'The republic exists because an army followed Marshal Popov to Tomsk, and the army knows it.'),
    'paranoia': ('generic_purge', [
        {'stability_factor': -0.03, 'research_speed_factor': -0.03},
        {'stability_factor': -0.06, 'research_speed_factor': -0.05, 'army_org_factor': -0.03},
        {'stability_factor': -0.10, 'research_speed_factor': -0.08, 'army_org_factor': -0.05},
    ], "The Vozhd's Paranoia", 'Everyone in Irkutsk chose him over Moscow. He trusts none of them, and there is nobody left to shoot.'),
    'army_lost': ('generic_army_problems', [
        {'army_morale_factor': -0.10},
    ], 'An Army That Lost', 'The divisions that followed him east were beaten all the way from the Volga.'),
    'whites': ('generic_guerilla_warfare', [
        {'stability_factor': -0.05, 'industrial_capacity_factory': -0.03},
        {'stability_factor': -0.10, 'industrial_capacity_factory': -0.06},
        {'stability_factor': -0.15, 'industrial_capacity_factory': -0.10, 'production_speed_buildings_factor': -0.10},
    ], 'Siberian White Army Remnant Resistance', "Kolchak's men never all went to Harbin. Their sons kept the rifles, and with the Red Army broken they have come out of the forest."),
    'organs': ('generic_secret_police', [
        {'political_power_gain': 0.05, 'stability_factor': -0.05},
        {'political_power_gain': 0.10, 'stability_factor': -0.08, 'war_support_factor': -0.05},
        {'political_power_gain': 0.15, 'stability_factor': -0.12, 'war_support_factor': -0.08},
    ], 'The Organs Rule', 'The Commissariat is the state. The party, the soviets and the army all answer to it.'),
    'fear': ('generic_oppression', [
        {'war_support_factor': -0.05, 'conscription_factor': -0.05},
        {'war_support_factor': -0.10, 'conscription_factor': -0.08},
        {'war_support_factor': -0.15, 'conscription_factor': -0.12},
    ], 'Fear of the Commissar', 'Nobody in the Urals says what he thinks, and nobody fights harder than he must.'),
    'cut_off': ('generic_disjointed_gov', [
        {'research_speed_factor': -0.10, 'production_factory_efficiency_gain_factor': -0.10},
    ], 'Cut Off from the Union', 'The Urals were the arsenal of a country that no longer exists.'),
}

# Starting spirits and the tier each starts at.
START = {
    'CSR': [('anarchists', 1), ('church', 1), ('food', 2), ('soldiers_republic', 2)],
    'FES': [('paranoia', 1), ('food', 2), ('army_lost', 1), ('whites', 1)],
    'WSM': [('organs', 1), ('fear', 1), ('cut_off', 1)],
}

# Plain bonus ideas granted by focuses.
IDEAS = {
    'wif_csr_duma': ('generic_democratic_drift_bonus', {'political_power_gain': 0.10}, 'The Siberian Duma', 'Four hundred deputies in a cold merchants\' club in Tomsk.'),
    'wif_csr_ruble': ('generic_devalue_currency', {'consumer_goods_factor': -0.05}, 'The Siberian Ruble', 'Tomsk prints its own money.'),
    'wif_csr_miners_fed': ('generic_production_bonus', {'industrial_capacity_factory': 0.05}, 'Miners Fed First', 'No coal without miners, no miners without bread.'),
    'wif_csr_siberian_rifles': ('generic_infantry_bonus', {'army_org_factor': 0.05}, 'Siberian Rifle Divisions', 'The divisions that saved Moscow in 1941 came from here.'),
    'wif_csr_plans_east_idea': ('generic_war_preparation', {'army_attack_factor': 0.05}, 'Plans for the East', 'The arrows on the staff maps all point at Irkutsk.'),
    'wif_fes_by_telephone_idea': ('generic_disjointed_gov', {'political_power_factor': -0.10}, 'Rule by Telephone', 'Orders come down the line at three in the morning.'),
    'wif_fes_doctors_idea': ('generic_prisoner', {'research_speed_factor': -0.05}, 'Doctors Under Suspicion', 'Even the men who take his pulse might be poisoners.'),
    'wif_fes_vozhd_alone_idea': ('generic_pp_unity_bonus', {'political_power_gain': 0.10}, 'The Vozhd Alone', 'Loyal men all around him, and he trusts none of them.'),
    'wif_fes_fronts_idea': ('generic_army_war_college', {'army_org_factor': 0.05}, 'The Fronts Re-formed', 'Transbaikal Front, Far Eastern Front - the old names, the old staffs.'),
    'wif_fes_plan_west_idea': ('generic_war_preparation', {'army_attack_factor': 0.05}, 'Plan West', 'The arrows on the staff maps all point at Tomsk.'),
    'wif_wsm_party_answers_idea': ('generic_secret_police', {'political_power_gain': 0.05}, 'The Party Answers to the Organs', 'Every party committee has an NKVD officer, and he signs the minutes.'),
    'wif_wsm_curfew_idea': ('generic_oppression', {'stability_factor': 0.05, 'industrial_capacity_factory': -0.05}, 'The Long Curfew', 'Off the streets at nine. Lights out at ten.'),
    'wif_wsm_special_depts_idea': ('generic_secret_police', {'army_org_factor': -0.05}, 'The Special Departments', 'An NKVD officer in every regiment, answering only to Tyumen.'),
    'wif_wsm_institute': ('generic_research_bonus', {'research_speed_factor': 0.05}, 'The Institute Seized', 'NKVD troops hold the Institute for All Research at Chelyabinsk.'),
    'wif_wsm_under_guard_idea': ('generic_prisoner', {'research_speed_factor': 0.05, 'stability_factor': -0.05}, 'Scientists Under Guard', 'They work, eat and sleep inside the wire.'),
    'wif_wsm_prisoners_invent_idea': ('generic_research_bonus', {'research_speed_factor': 0.05}, 'Prisoners Who Invent', 'The sharashka\'s best engineers are promised their freedom.'),
    'wif_wsm_plan': ('generic_production_bonus', {'production_speed_buildings_factor': 0.05, 'industrial_capacity_factory': 0.05}, "The Commissariat's Plan", 'A five-year plan drawn up by policemen.'),
    'wif_wsm_border_guards_idea': ('generic_fortify_the_borders', {'army_core_defence_factor': 0.05}, 'The Border Guard Divisions', 'NKVD border guards, the best-equipped soldiers in the Urals.'),
}
TIMED = {'wif_csr_plans_east_idea': 365, 'wif_fes_plan_west_idea': 365, 'wif_fes_doctors_idea': 365}


# ------------------------------------------------------------ reward helpers
def grow(s): return f'wif_sib_{s}_grow = yes'
def ease(s): return f'wif_sib_{s}_ease = yes'
def worst(s): return f'wif_sib_{s}_max = yes'
def remove(s): return f'wif_sib_{s}_remove = yes'
def idea(k): return f'add_timed_idea = {{ idea = {k} days = {TIMED[k]} }}' if k in TIMED else f'add_ideas = {k}'
def pp(n): return f'add_political_power = {n}'
def stab(n): return f'add_stability = {n}'
def ws(n): return f'add_war_support = {n}'
def pop(ide, n): return f'add_popularity = {{ ideology = {ide} popularity = {n} }}'
def xp(n): return f'army_experience = {n}'
def mp(n): return f'add_manpower = {n}'
def stock(kind, n): return f'add_equipment_to_stockpile = {{ type = {kind} amount = {n} producer = ROOT }}'
def bonus(cat, uses=1, b=0.5, name=None): return f'add_tech_bonus = {{ name = {name or "wif_sib_" + cat} bonus = {b} uses = {uses} category = {cat} }}'


def build(kind, state=None):
    body = ('add_extra_state_shared_building_slots = 1\n'
            f'add_building_construction = {{ type = {kind} level = 1 instant_build = yes }}')
    if state is None:
        return 'capital_scope = {\n' + indent(body, 1) + '\n}'
    return (f'if = {{\n\tlimit = {{ {state} = {{ is_owned_by = ROOT }} }}\n\t{state} = {{\n{indent(body, 2)}\n\t}}\n}}\n'
            f'else = {{\n\tcapital_scope = {{\n{indent(body, 2)}\n\t}}\n}}')


def steel(n, state=None):
    body = f'add_resource = {{ type = steel amount = {n} }}'
    if state is None:
        return 'capital_scope = { ' + body + ' }'
    return (f'if = {{ limit = {{ {state} = {{ is_owned_by = ROOT }} }} {state} = {{ {body} }} }}\n'
            f'else = {{ capital_scope = {{ {body} }} }}')


def border_forts(enemy=None):
    lim = f'any_neighbor_state = {{ is_owned_by = {enemy} }}' if enemy else 'is_border_state = yes'
    return ('every_owned_state = {\n\tlimit = { ' + lim + ' }\n'
            '\tadd_building_construction = {\n\t\ttype = bunker\n\t\tlevel = 1\n'
            '\t\tprovince = { all_provinces = yes limit_to_border = yes }\n\t\tinstant_build = yes\n\t}\n}')


def war(target):
    return (f'if = {{\n\tlimit = {{ country_exists = {target} NOT = {{ has_war_with = {target} }} }}\n'
            f'\tdeclare_war_on = {{ target = {target} type = annex_everything }}\n'
            '\tset_global_flag = wif_siberian_war\n'
            '\t# A month later both states collapse (tools/gen_siberia_collapse.py).\n'
            '\tcountry_event = { id = wif_sibc.1 days = 30 }\n}')


def j(*xs):
    return '\n'.join(xs)


R = {
    'CSR': {
        'tomsk_declaration': stab(0.05),
        'provisional': pp(50),
        'assembly': stab(0.05),
        'parties': pop('democratic', 0.10),
        'press': j(stab(0.05), ws(-0.05)),
        'campaign': pp(25),
        'election': j('set_politics = { ruling_party = democratic elections_allowed = yes }', 'hold_election = ROOT', stab(0.10)),
        'coalition': j(stab(0.10), ws(-0.05), remove('soldiers_republic')),
        'marshals_bloc': j(ws(0.10), ease('soldiers_republic')),
        'duma_seated': idea('wif_csr_duma'),
        'constitution': stab(0.10),
        'banners_spread': grow('anarchists'),
        'rail_sabotage': worst('anarchists'),
        'sermons': grow('church'),
        'blessing': j(worst('church'), pop('democratic', -0.05)),
        'refugees': j(mp(20000), stab(-0.05)),
        'zemstvo': stab(0.05),
        'land_question': j(stab(0.05), pop('democratic', 0.05)),
        'siberian_ruble': idea('wif_csr_ruble'),
        'army_oath': j(stab(0.05), ws(0.05)),
        'grain_census': pp(25),
        'rationing': j(ease('food'), stab(-0.05)),
        'requisition': j(ease('food'), stab(-0.05)),
        'free_markets': j(ease('food'), pp(25)),
        'kuzbass_fed': idea('wif_csr_miners_fed'),
        'harvest': remove('food'),
        'popovs_army': xp(25),
        'kuzbass': j(build('industrial_complex', 40), steel(2, 40)),
        'novosibirsk': build('arms_factory', 570),
        'rifles': idea('wif_csr_siberian_rifles'),
        'yenisei': border_forts('FES'),
        'plans_east': idea('wif_csr_plans_east_idea'),
        'march_east': war('FES'),
    },
    'FES': {
        'irkutsk': stab(0.05),
        'vozhd': pp(50),
        'portraits': pop('communism', 0.10),
        'pravda_east': ws(0.05),
        'cult': stab(0.10),
        'betrayed': j(ws(0.10), stab(-0.05)),
        'loyal_marshals': xp(50),
        'union_lives': ('if = {\n\tlimit = { country_exists = CSR }\n\tCSR = {\n'
                        '\t\tevery_owned_state = { add_claim_by = FES }\n\t}\n}'),
        'whites_taiga': grow('whites'),
        'amur_ambush': worst('whites'),
        'atamans_banner': j(worst('whites'), stab(-0.05)),
        'the_few': j(grow('paranoia'), pp(50)),
        'sleeps_badly': grow('paranoia'),
        'tasters': stab(-0.05),
        'by_telephone': j(ease('paranoia'), idea('wif_fes_by_telephone_idea')),
        'show_himself': j(ws(0.10), grow('paranoia')),
        'papers': stab(-0.05),
        'doctors': j(grow('paranoia'), idea('wif_fes_doctors_idea')),
        'vozhd_alone': j(worst('paranoia'), idea('wif_fes_vozhd_alone_idea')),
        'shadows': grow('paranoia'),
        'hungry_winter': grow('food'),
        'kolkhoz': ease('food'),
        'raise_quotas': j(ease('food'), stab(-0.05)),
        'private_plots': j(ease('food'), pop('communism', -0.05)),
        'okhotsk_fish': ease('food'),
        'buryat_grain': remove('food'),
        'manchurian_rice': j(pp(50), stab(0.03)),
        'forty_percent': xp(25),
        'fronts': idea('wif_fes_fronts_idea'),
        'trans_siberian': ('every_owned_state = {\n\tlimit = { OR = { state = 566 state = 564 state = 563 state = 561 } }\n'
                           '\tadd_building_construction = { type = infrastructure level = 1 instant_build = yes }\n}'),
        'amur_works': build('arms_factory', 561),
        'ulan_ude_guns': stock('artillery_equipment', 150),
        'plan_west': idea('wif_fes_plan_west_idea'),
        'hang_popov': war('CSR'),
    },
    'WSM': {
        'commissar': stab(0.05),
        'proclaim': pp(50),
        'sverdlovsk_soviet': j(stab(-0.05), ws(0.05)),
        'party_answers': idea('wif_wsm_party_answers_idea'),
        'through_party': j(pop('communism', 0.10), stab(0.05)),
        'through_organs': j(grow('organs'), pp(50)),
        'order_state': j(stab(0.10), ws(-0.05)),
        'registered': j(stab(0.05), mp(10000)),
        'passports': stab(-0.05),
        'curfew': idea('wif_wsm_curfew_idea'),
        'one_voice': ws(0.10),
        'portraits': stab(0.05),
        'no_successor': j(stab(-0.05), pp(50)),
        'grip_tightens': j(stab(0.10), worst('organs')),
        'absolute_order': j('set_country_flag = wif_wsm_absolute_order', pp(100),
                            '# The Marxists collapse (tools/gen_siberia_collapse.py).',
                            'country_event = { id = wif_sibc.2 days = 1 }'),
        'rebuild_organs': pp(50),
        'informers': j(stab(0.05), ws(-0.05)),
        'special_depts': idea('wif_wsm_special_depts_idea'),
        'camps': j(mp(15000), stab(-0.05)),
        'files': pp(25),
        'open_terror': j(grow('fear'), stab(0.05)),
        'quiet_watch': ease('fear'),
        'watchers': stab(0.05),
        'yagodas_guard': j(xp(15), stock('infantry_equipment', 1000)),
        'whispers': stab(-0.05),
        'officers_resent': j(stab(-0.05), ws(-0.05)),
        'cracks': stab(-0.10),
        'seize_institute': idea('wif_wsm_institute'),
        'under_guard': idea('wif_wsm_under_guard_idea'),
        'sharashka': j(bonus('industry'), bonus('infantry_weapons')),
        'weapons_for_organs': j(bonus('infantry_weapons', 2, name='wif_wsm_weapons'), bonus('support_tech', 1, name='wif_wsm_support')),
        'machines': bonus('industry', 2, name='wif_wsm_machines_bonus'),
        'kyshtym': bonus('nuclear', 1, name='wif_wsm_kyshtym_bonus'),
        'prisoners_invent': idea('wif_wsm_prisoners_invent_idea'),
        'uralmash': build('industrial_complex', 653),
        'tankograd': build('arms_factory', 572),
        'prison_labour': j(steel(4, 653), stab(-0.05)),
        'tobolsk_grain': stab(0.05),
        'sverdlovsk_arms': build('arms_factory', 653),
        'loyal_rations': j(stab(0.05), grow('fear')),
        'commissariat_plan': idea('wif_wsm_plan'),
        'nkvd_troops': xp(25),
        'border_guards': idea('wif_wsm_border_guards_idea'),
        'ural_passes': border_forts(),
        'tankograd_tanks': j(xp(25), stock('motorized_equipment', 100)),
    },
}

ICON_BY_BRANCH = {'political': 'political_pressure', 'inner': 'propaganda', 'economy': 'consumer_goods',
                  'industry': 'construct_civ_factory', 'military': 'army_doctrines', 'diplomacy': 'improve_relations',
                  'project': 'secret_weapon'}
ICON = {
    'march_east': 'major_war', 'hang_popov': 'major_war', 'absolute_order': 'national_unity',
    'election': 'neutrality_focus', 'constitution': 'national_unity', 'duma_seated': 'neutrality_focus',
    'harvest': 'consumer_goods', 'buryat_grain': 'consumer_goods', 'rationing': 'consumer_goods',
    'kuzbass': 'construct_civ_factory', 'novosibirsk': 'construct_mil_factory', 'amur_works': 'construct_mil_factory',
    'tankograd': 'construct_mil_factory', 'sverdlovsk_arms': 'construct_mil_factory', 'uralmash': 'construct_civ_factory',
    'yenisei': 'defence', 'ural_passes': 'defence', 'trans_siberian': 'construct_infrastructure',
    'ulan_ude_guns': 'army_artillery', 'tankograd_tanks': 'army_motorized', 'rifles': 'allies_build_infantry',
    'seize_institute': 'secret_weapon', 'sharashka': 'scientific_exchange', 'kyshtym': 'secret_weapon',
    'cult': 'national_unity', 'portraits': 'propaganda', 'vozhd_alone': 'political_pressure',
}
FILTER = {'political': 'FOCUS_FILTER_POLITICAL', 'inner': 'FOCUS_FILTER_STABILITY',
          'diplomacy': 'FOCUS_FILTER_POLITICAL', 'military': 'FOCUS_FILTER_ARMY_XP',
          'industry': 'FOCUS_FILTER_INDUSTRY', 'economy': 'FOCUS_FILTER_INDUSTRY',
          'project': 'FOCUS_FILTER_RESEARCH'}

TREES = {
    'CSR': ('planner_csr.json', 'wif_csr_focus', 'common/scripted_effects/wif_central_siberia.txt',
            '\t\tCSR = {\n\t\t\tset_capital = { state = 578 }\t\t\t# Tomsk\n'),
    'FES': ('planner_fes.json', 'wif_fes_focus', 'common/scripted_effects/wif_far_east.txt',
            '\t\tFES = {\n\t\t\tset_capital = { state = 566 }\t\t\t# Irkutsk\n'),
    'WSM': ('planner_wsm.json', 'wif_wsm_focus', 'common/scripted_effects/wif_west_siberia.txt',
            '\t\tWSM = {\n'),
}


def load(tag):
    m = json.load(open(p('tools', TREES[tag][0]), encoding='utf-8'))
    pre = f'wif_{tag.lower()}_'
    by_id = {f['id']: f for f in m['focuses']}
    for f in m['focuses']:
        f['key'] = f['fid'][len(pre):]
        assert f['key'] in R[tag], f'{tag}: no reward for {f["fid"]}'
    return m, by_id


def gen_tree(tag, m, by_id):
    tid = TREES[tag][1]
    o = ['# GENERATED by tools/gen_siberia_trees.py from the Focus Tree Planner',
         f'# (tools/{TREES[tag][0]}) - do not edit by hand.', '',
         'focus_tree = {', f'\tid = {tid}', '',
         '\tcountry = {', '\t\tfactor = 0', '\t\tmodifier = {', '\t\t\tadd = 100', f'\t\t\ttag = {tag}', '\t\t}', '\t}', '',
         '\tdefault = no',
         # below the lowest focus: the 770x380 continuous window covers the top-left otherwise
         f'\tcontinuous_focus_position = {{ x = 50 y = {(max(f["y"] for f in m["focuses"]) + 2) * 130} }}', '']
    for f in sorted(m['focuses'], key=lambda f: (f['y'], f['x'])):
        k = f['key']
        o.append('\tfocus = {')
        o.append(f'\t\tid = {f["fid"]}')
        o.append(f'\t\ticon = GFX_goal_generic_{ICON.get(k, ICON_BY_BRANCH[f["branch"]])}')
        if f['pre']:
            ids = [by_id[i]['fid'] for i in f['pre']]
            if f['any']:
                o.append('\t\tprerequisite = { ' + ' '.join(f'focus = {i}' for i in ids) + ' }')
            else:
                o += [f'\t\tprerequisite = {{ focus = {i} }}' for i in ids]
        if f['mx']:
            o.append('\t\tmutually_exclusive = { ' + ' '.join(f'focus = {by_id[i]["fid"]}' for i in f['mx']) + ' }')
        o.append(f'\t\tx = {f["x"]}')
        o.append(f'\t\ty = {f["y"]}')
        if f.get('auto'):
            # Never the player's: only wif_sib_auto_<TAG> sets this flag, the
            # moment before it completes the focus itself.
            o.append(f'\t\tcost = 1')
            o.append(f'\t\tavailable = {{ has_country_flag = wif_sib_auto_{f["fid"]} }}')
            o.append('\t\tai_will_do = { factor = 0 }')
        else:
            o.append(f'\t\tcost = {cost(f["days"])}')
            o.append(f'\t\tai_will_do = {{ factor = {5 if f["mx"] else 10} }}')
        o.append(f'\t\tsearch_filters = {{ {FILTER[f["branch"]]} }}')
        o.append('\t\tcompletion_reward = {')
        o.append(indent(R[tag][k], 3))
        o.append('\t\t}')
        o.append('\t}')
        o.append('')
    o.append('}')
    o.append('')
    write(f'common/national_focus/{tid}.txt', '\n'.join(o))


def spirit_id(s, t, n):
    return f'wif_sib_{s}' if n == 1 else f'wif_sib_{s}_{t}'


def gen_ideas():
    o = ['# GENERATED by tools/gen_siberia_trees.py - do not edit by hand.', '',
         'ideas = {', '\tcountry = {']
    for s, (pic, tiers, _, _) in SPIRITS.items():
        for t, mods in enumerate(tiers, 1):
            o += [f'\t\t{spirit_id(s, t, len(tiers))} = {{', f'\t\t\tpicture = {pic}',
                  '\t\t\tallowed = { always = no }', '\t\t\tallowed_civil_war = { always = yes }',
                  '\t\t\tremoval_cost = -1', '\t\t\tmodifier = {']
            o += [f'\t\t\t\t{a} = {b}' for a, b in mods.items()]
            o += ['\t\t\t}', '\t\t}']
    for k, (pic, mods, _, _) in IDEAS.items():
        o += [f'\t\t{k} = {{', f'\t\t\tpicture = {pic}', '\t\t\tallowed = { always = no }',
              '\t\t\tremoval_cost = -1', '\t\t\tmodifier = {']
        o += [f'\t\t\t\t{a} = {b}' for a, b in mods.items()]
        o += ['\t\t\t}', '\t\t}']
    o += ['\t}', '}', '']
    write('common/ideas/wif_siberia_ideas.txt', '\n'.join(o))


def gen_effects(maps):
    o = ['# GENERATED by tools/gen_siberia_trees.py - do not edit by hand.', '']
    # tier movers
    for s, (_, tiers, _, _) in SPIRITS.items():
        n = len(tiers)
        ids = [spirit_id(s, t, n) for t in range(1, n + 1)]
        o.append(f'# {SPIRITS[s][2]}: {" < ".join(ids)}')
        # grow: up one tier, or start at the bottom
        o.append(f'wif_sib_{s}_grow = {{')
        first = True
        for a, b in zip(ids[-2::-1], ids[:0:-1]):
            o.append(f'\t{"if" if first else "else_if"} = {{ limit = {{ has_idea = {a} }} swap_ideas = {{ remove_idea = {a} add_idea = {b} }} }}')
            first = False
        cond = ' '.join(f'has_idea = {i}' for i in ids)
        o.append(f'\t{"if" if first else "else_if"} = {{ limit = {{ NOT = {{ OR = {{ {cond} }} }} }} add_ideas = {ids[0]} }}')
        o.append('}')
        o.append(f'wif_sib_{s}_ease = {{')
        first = True
        for a, b in zip(ids[:0:-1], ids[-2::-1]):
            o.append(f'\t{"if" if first else "else_if"} = {{ limit = {{ has_idea = {a} }} swap_ideas = {{ remove_idea = {a} add_idea = {b} }} }}')
            first = False
        if first:
            o.append('\t# one tier only: easing does nothing')
        o.append('}')
        o.append(f'wif_sib_{s}_max = {{')
        o += [f'\tif = {{ limit = {{ has_idea = {i} }} remove_ideas = {i} }}' for i in ids[:-1]]
        o.append(f'\tif = {{ limit = {{ NOT = {{ has_idea = {ids[-1]} }} }} add_ideas = {ids[-1]} }}')
        o.append('}')
        o.append(f'wif_sib_{s}_remove = {{')
        o += [f'\tif = {{ limit = {{ has_idea = {i} }} remove_ideas = {i} }}' for i in ids]
        o.append('}')
        o.append('')
    # setup per tag
    for tag in TREES:
        o.append(f'# {tag} scope, once, when the country forms. Starting spirits and the tree.')
        o.append(f'wif_sib_setup_{tag} = {{')
        o.append(f'\tload_focus_tree = {{ tree = {TREES[tag][1]} keep_completed = no }}')
        for s, t in START[tag]:
            n = len(SPIRITS[s][1])
            o.append(f'\tif = {{ limit = {{ NOT = {{ has_idea = {spirit_id(s, t, n)} }} }} add_ideas = {spirit_id(s, t, n)} }}')
        o.append('}')
        o.append('')
    # auto-focus timers
    for tag, (m, by_id) in maps.items():
        o.append(f'# {tag} scope, weekly. The focuses that do themselves: once the')
        o.append('# prerequisites are done, count the planner days, then complete.')
        o.append(f'wif_sib_auto_{tag} = {{')
        for f in m['focuses']:
            if not f.get('auto'):
                continue
            fid = f['fid']
            ids = [by_id[i]['fid'] for i in f['pre']]
            if not ids:
                req = ''
            elif f['any'] and len(ids) > 1:
                req = ' OR = { ' + ' '.join(f'has_completed_focus = {i}' for i in ids) + ' }'
            else:
                req = ' ' + ' '.join(f'has_completed_focus = {i}' for i in ids)
            o += [f'\tif = {{',
                  f'\t\tlimit = {{ NOT = {{ has_completed_focus = {fid} }}{req} }}',
                  f'\t\tadd_to_variable = {{ wif_sib_t_{fid} = 7 }}',
                  f'\t\tif = {{',
                  f'\t\t\tlimit = {{ check_variable = {{ wif_sib_t_{fid} > {f["days"] - 1} }} }}',
                  f'\t\t\tset_country_flag = wif_sib_auto_{fid}',
                  f'\t\t\tcomplete_national_focus = {fid}',
                  f'\t\t}}',
                  f'\t}}']
        o.append('}')
        o.append('')
    write('common/scripted_effects/wif_siberia_effects.txt', '\n'.join(o))


def gen_on_actions():
    o = ['# GENERATED by tools/gen_siberia_trees.py - do not edit by hand.', '', 'on_actions = {']
    for tag in TREES:
        o += [f'\ton_weekly_{tag} = {{', '\t\teffect = {', f'\t\t\twif_sib_auto_{tag} = yes', '\t\t}', '\t}']
    o += ['}', '']
    write('common/on_actions/wif_siberia_on_actions.txt', '\n'.join(o))


def esc(s):
    return s.replace('\\n', '\n').replace('"', '\\"').replace('\n', '\\n')


def gen_loc(maps):
    o = ['l_english:']
    for tag, (m, _) in maps.items():
        for f in m['focuses']:
            flav = re.split(r'\n\nEffect:', f['desc'])[0].strip()
            o.append(f' {f["fid"]}:0 "{esc(f["name"])}"')
            o.append(f' {f["fid"]}_desc:0 "{esc(flav)}"')
    for s, (_, tiers, name, desc) in SPIRITS.items():
        n = len(tiers)
        for t in range(1, n + 1):
            suffix = '' if n == 1 else ['', ' (Rising)', ' (Severe)'][t - 1] if n == 3 else ['', ' (Strong)'][t - 1]
            o.append(f' {spirit_id(s, t, n)}:0 "{esc(name + suffix)}"')
            o.append(f' {spirit_id(s, t, n)}_desc:0 "{esc(desc)}"')
    for k, (_, _, name, desc) in IDEAS.items():
        o.append(f' {k}:0 "{esc(name)}"')
        o.append(f' {k}_desc:0 "{esc(desc)}"')
    for nm in ['wif_sib_industry', 'wif_sib_infantry_weapons', 'wif_wsm_weapons', 'wif_wsm_support', 'wif_wsm_machines_bonus', 'wif_wsm_kyshtym_bonus']:
        o.append(f' {nm}:0 "Siberian Research"')
    write('localisation/english/wif_siberia_l_english.yml', '\n'.join(o) + '\n', bom=True)


def splice_setup():
    for tag, (_, _, rel, anchor) in TREES.items():
        s = open(p(rel), 'rb').read().decode('utf-8')
        nl = '\r\n' if '\r\n' in s else '\n'
        call = f'\t\t\twif_sib_setup_{tag} = yes\t# tree + starting spirits, tools/gen_siberia_trees.py'
        if call in s:
            print('already spliced', rel)
            continue
        a = anchor.replace('\n', nl)
        assert s.count(a) >= 1, f'anchor missing in {rel}'
        s = s.replace(a, a + call + nl, 1)
        open(p(rel), 'wb').write(s.encode('utf-8'))
        print('spliced', rel)


def unblank():
    rel = 'common/national_focus/wif_breakaway_blank.txt'
    s = open(p(rel), 'rb').read().decode('utf-8')
    nl = '\r\n' if '\r\n' in s else '\n'
    for tag in TREES:
        line = f'\t\t\t\ttag = {tag}{nl}'
        if line in s:
            s = s.replace(line, '', 1)
            print('removed', tag, 'from the blank tree')
    open(p(rel), 'wb').write(s.encode('utf-8'))


if __name__ == '__main__':
    maps = {tag: load(tag) for tag in TREES}
    for tag, (m, by_id) in maps.items():
        gen_tree(tag, m, by_id)
    gen_ideas()
    gen_effects(maps)
    gen_on_actions()
    gen_loc(maps)
    splice_setup()
    unblank()
