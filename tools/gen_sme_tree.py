"""The SME's 1944-1952 continuation, as drawn in the Focus Tree Planner (map
sme-focus-tree; game x = planner x + 9).

Writes:
  common/national_focus/SME_focus.txt     between # >>> GENERATED / # <<< GENERATED
  common/ideas/wif_sme_tree_ideas.txt
  common/scripted_effects/wif_sme_tree_watchers.txt
  localisation/english/wif_sme_tree_l_english.yml

Watchers - focuses the planner draws dashed - complete themselves when Germany
does the matching thing: wif_sme_tree_watchers runs weekly (on_weekly_SME in
common/on_actions/wif_sme_war_on_actions.txt) and calls
complete_national_focus. The player can also take them by hand once
available; they cost two weeks.

Re-run tools/gen_sme_collapse.py afterwards: it collects every spirit the SME
can hold, so the new ones are stripped when the SME collapses.
"""
import math
import os
import re

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(*a):
    return os.path.join(MOD, *a)


def cost(days):
    # Weeks, rounded UP to three decimals so the game's floor shows the right day.
    w = days / 7
    if abs(w - round(w)) < 1e-9:
        return str(int(round(w)))
    return f'{math.ceil(w * 1000) / 1000:.3f}'


def owned(state, body):
    return f'if = {{\n\tlimit = {{ {state} = {{ is_owned_by = ROOT }} }}\n\t{state} = {{\n{indent(body, 2)}\n\t}}\n}}'


def indent(text, n):
    return '\n'.join(('\t' * n + l) if l else l for l in text.split('\n'))


def build(btype, level, province=None):
    prov = f'\nprovince = {{ {province} }}' if province else ''
    return (f'add_extra_state_shared_building_slots = {level}\n' if btype in ('industrial_complex', 'arms_factory', 'dockyard') else '') + \
        f'add_building_construction = {{\n\ttype = {btype}\n\tlevel = {level}{indent(prov, 1)}\n\tinstant_build = yes\n}}'


def spread(btype, n, states):
    ors = ' '.join(f'state = {s}' for s in states)
    one = (f'random_owned_controlled_state = {{\n\tlimit = {{ OR = {{ {ors} }} }}\n'
           f'{indent(build(btype, 1), 1)}\n}}')
    return '\n'.join([one] * n)


URALS = [653, 572, 582, 573, 651, 652, 398, 1082]
SIBERIA = [570, 571, 578, 403, 580, 577, 568]

# id, name, x, y, days, icon, prerequisites (list of OR-groups), extra keys
F = []


def focus(id_, name, x, y, days, icon, pre=(), desc='', reward='', mx=(), available='', auto=None,
          filt='FOCUS_FILTER_POLITICAL', ai=10, bypass=''):
    F.append(dict(id=id_, name=name, x=x, y=y, days=days, icon=icon, pre=[list(g) for g in pre], desc=desc,
                  reward=reward, mx=list(mx), available=available, auto=auto, filt=filt, ai=ai, bypass=bypass))


# ----------------------------------------------------------------- political
focus('SME_take_down_the_fascists', 'Take Down the Fascists, Use Their Printers', 15, 12, 70,
      'GFX_goal_generic_propaganda', [['SME_our_will_towards_the_second_trial']],
      'The fascist papers the Emergency Government tolerated are closed, and their presses print for the Party instead.',
      'if = {\n\tlimit = { has_idea = wif_sme_fascist_writers }\n\tswap_ideas = { remove_idea = wif_sme_fascist_writers add_idea = wif_sme_fascist_writers_turned }\n}\n'
      'else = {\n\tadd_ideas = wif_sme_fascist_writers_turned\n}')
focus('SME_sverdlovsk_congress', 'The Sverdlovsk Congress', 15, 13, 50, 'GFX_goal_generic_national_unity',
      [['SME_take_down_the_fascists']],
      'The first Party congress since the coup.',
      'add_stability = 0.10\nadd_popularity = { ideology = communism popularity = 0.10 }')
focus('SME_komsomol_returns', 'The Komsomol Returns', 14, 14, 35, 'GFX_goal_generic_allies_build_infantry',
      [['SME_sverdlovsk_congress']], 'The Young Communist League reopens its offices in every Ural town.',
      'add_war_support = 0.05\nadd_ideas = wif_sme_komsomol', filt='FOCUS_FILTER_MANPOWER')
focus('SME_one_russia', 'One Russia', 16, 14, 35, 'GFX_goal_generic_more_territorial_claims',
      [['SME_sverdlovsk_congress']], 'Every Russian under the commissars is a citizen waiting to come home.',
      'every_state = {\n\tlimit = {\n\t\tis_owned_by = RKM\n\t\tOR = { is_core_of = SOV is_core_of = SME }\n\t}\n\tadd_state_claim = ROOT\n}',
      filt='FOCUS_FILTER_ANNEXATION')
focus('SME_heir_to_the_union', 'Heir to the Union', 15, 15, 50, 'GFX_goal_generic_soviet_construction',
      [['SME_komsomol_returns'], ['SME_one_russia']],
      'The Emergency Government stops calling itself temporary.',
      'add_ideas = wif_sme_heir_to_the_union', filt='FOCUS_FILTER_STABILITY')

# ----------------------------------------------------------------- industry
focus('SME_the_evacuated_factories', 'The Evacuated Factories', 26, 4, 50, 'GFX_goal_generic_construct_civ_factory',
      [['SME_industries_of_siberia']],
      'The plants carried east in 1941 are finally rebuilt as factories rather than sheds.',
      owned(653, build('industrial_complex', 2)), filt='FOCUS_FILTER_INDUSTRY')
focus('SME_tankograd', 'Tankograd', 25, 5, 50, 'GFX_goal_generic_army_tanks', [['SME_the_evacuated_factories']],
      'The Kirov works in Chelyabinsk go back to building tanks.',
      owned(572, build('arms_factory', 2)) + '\nadd_tech_bonus = {\n\tname = SME_tankograd\n\tbonus = 0.10\n\tuses = 2\n\tcategory = armor\n}',
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_magnitogorsk_steel', 'Magnitogorsk Steel', 27, 5, 50, 'GFX_goal_generic_production',
      [['SME_the_evacuated_factories']], 'The blast furnaces on the Ural river are relit.',
      owned(582, 'add_resource = {\n\ttype = steel\n\tamount = 12\n}\nadd_extra_state_shared_building_slots = 1'),
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_a_plan_for_restoration', 'A Plan for Restoration', 26, 6, 50, 'GFX_goal_generic_construction',
      [['SME_tankograd'], ['SME_magnitogorsk_steel']], 'Gosplan, or what is left of it, draws up a plan.',
      'add_timed_idea = { idea = wif_sme_plan_for_restoration days = 730 }', filt='FOCUS_FILTER_INDUSTRY')
focus('SME_guns_first', 'Guns First', 25, 7, 35, 'GFX_goal_generic_construct_mil_factory',
      [['SME_a_plan_for_restoration']], 'Moscow first. Bread afterwards.',
      spread('arms_factory', 3, URALS) + '\nadd_stability = -0.05', mx=['SME_bread_first'], filt='FOCUS_FILTER_INDUSTRY')
focus('SME_bread_first', 'Bread First', 27, 7, 35, 'GFX_goal_generic_consumer_goods',
      [['SME_a_plan_for_restoration']], 'An army marches on a full country.',
      spread('industrial_complex', 3, SIBERIA) + '\nadd_stability = 0.05', mx=['SME_guns_first'], filt='FOCUS_FILTER_INDUSTRY')
focus('SME_dams_on_the_ob', 'Dams on the Ob', 26, 8, 50, 'GFX_goal_generic_construct_infrastructure',
      [['SME_guns_first', 'SME_bread_first']], 'Novosibirsk gets its power station.',
      owned(570, build('industrial_complex', 1) + '\n' + build('infrastructure', 1)) + '\nadd_ideas = wif_sme_ural_industry',
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_fourth_five_year_plan', 'The Fourth Five-Year Plan', 26, 9, 50, 'GFX_goal_generic_production2',
      [['SME_dams_on_the_ob']], 'The plan Moscow never got to write.',
      'add_research_slot = 1\nif = {\n\tlimit = { has_idea = wif_sme_ural_industry }\n\tswap_ideas = { remove_idea = wif_sme_ural_industry add_idea = wif_sme_ural_industry_2 }\n}\n'
      'else = {\n\tadd_ideas = wif_sme_ural_industry_2\n}', filt='FOCUS_FILTER_RESEARCH')
focus('SME_chelyabinsk_40', 'Chelyabinsk-40', 26, 10, 50, 'GFX_goal_generic_secret_weapon',
      [['SME_fourth_five_year_plan'], ['SME_chelyabinsk_institute']],
      'Laboratory No. 2 is rebuilt behind wire outside Kyshtym.',
      'add_ideas = wif_sme_chelyabinsk_40\n' + owned(572, 'add_building_construction = {\n\ttype = nuclear_reactor\n\tlevel = 1\n\tinstant_build = yes\n}'),
      filt='FOCUS_FILTER_RESEARCH')

# ----------------------------------------------------------------- military
focus('SME_lessons_of_the_war', 'Lessons of the Great Patriotic War', 31, 6, 50, 'GFX_goal_generic_army_doctrines',
      [['SME_zlatoust_ural_military_district']], 'Every officer who survived 1941 is asked what went wrong.',
      'army_experience = 100\nadd_doctrine_cost_reduction = {\n\tname = SME_lessons_of_the_war\n\tcost_reduction = 0.25\n\tuses = 1\n\tcategory = land_doctrine\n}',
      filt='FOCUS_FILTER_ARMY_XP')
focus('SME_frunze_academy', 'The Frunze Academy in Sverdlovsk', 30, 7, 35, 'GFX_goal_generic_special_forces',
      [['SME_lessons_of_the_war']], 'The staff college reopens in exile.',
      'every_army_leader = {\n\trandom_list = {\n\t\t50 = { add_planning = 1 }\n\t\t50 = { add_logistics = 1 }\n\t}\n}\n'
      'if = {\n\tlimit = { NOT = { has_character = SOV_ivan_konev } }\n\tcreate_field_marshal = {\n\t\tname = "Ivan Konev"\n'
      '\t\tportrait_path = "gfx/leaders/SOV/portrait_SOV_ivan_konev.dds"\n\t\ttraits = { }\n\t\tskill = 4\n\t\tattack_skill = 4\n'
      '\t\tdefense_skill = 3\n\t\tplanning_skill = 3\n\t\tlogistics_skill = 3\n\t}\n}', filt='FOCUS_FILTER_ARMY_XP')
focus('SME_mechanised_corps_reborn', 'Mechanised Corps Reborn', 32, 7, 50, 'GFX_goal_generic_army_motorized',
      [['SME_lessons_of_the_war']], 'The mechanised corps of 1941 were broken up after the summer. They come back.',
      'add_tech_bonus = {\n\tname = SME_mechanised_corps_reborn\n\tbonus = 0.15\n\tuses = 2\n\tcategory = motorized_equipment\n\tcategory = cat_mechanized_equipment\n}',
      filt='FOCUS_FILTER_RESEARCH')
focus('SME_red_air_force_again', 'A Red Air Force Again', 30, 8, 50, 'GFX_goal_generic_build_airforce',
      [['SME_frunze_academy']], 'Airfields around Sverdlovsk, and pilots to fly from them.',
      owned(653, 'add_building_construction = {\n\ttype = air_base\n\tlevel = 2\n\tinstant_build = yes\n}') +
      '\nadd_tech_bonus = {\n\tname = SME_red_air_force_again\n\tbonus = 0.15\n\tuses = 2\n\tcategory = air_equipment\n}',
      filt='FOCUS_FILTER_AIR_XP')
focus('SME_the_ural_line', 'The Ural Line', 32, 8, 50, 'GFX_goal_generic_defence', [['SME_mechanised_corps_reborn']],
      'Bunkers along the border with Moskowien, while there is still peace to build them in.',
      'every_owned_state = {\n\tlimit = { any_neighbor_state = { is_owned_by = RKM } }\n\tadd_building_construction = {\n\t\ttype = bunker\n\t\tlevel = 2\n'
      '\t\tprovince = { all_provinces = yes limit_to_border = yes }\n\t\tinstant_build = yes\n\t}\n}',
      available='NOT = { has_war_with = RKM }', filt='FOCUS_FILTER_ARMY_XP')
focus('SME_deep_battle_restored', 'Deep Battle Restored', 31, 9, 50, 'GFX_goal_generic_army_artillery2',
      [['SME_red_air_force_again'], ['SME_the_ural_line']], "Tukhachevsky's doctrine, without Tukhachevsky.",
      'add_timed_idea = { idea = wif_sme_deep_battle days = 730 }', filt='FOCUS_FILTER_ARMY_XP')
focus('SME_plan_kutuzov', 'Plan Kutuzov', 31, 10, 50, 'GFX_goal_generic_occupy_start_war',
      [['SME_deep_battle_restored'], ['SME_total_mobilisation', 'SME_heir_to_the_union']],
      'The plan to take back Moscow.',
      'every_state = {\n\tlimit = {\n\t\tis_owned_by = RKM\n\t\tis_core_of = ROOT\n\t}\n\tadd_state_claim = ROOT\n}\nadd_ideas = wif_sme_plan_kutuzov',
      filt='FOCUS_FILTER_ARMY_XP')
focus('SME_the_road_to_moscow', 'The Road to Moscow', 31, 11, 35, 'GFX_goal_generic_major_war',
      [['SME_plan_kutuzov'], ['SME_the_hour_has_come']], 'Forward.',
      'add_war_support = 0.20\nevery_controlled_state = {\n\tlimit = { is_owned_by = RKM }\n\tadd_core_of = ROOT\n}',
      available='has_war_with = RKM', filt='FOCUS_FILTER_WAR_SUPPORT')

# ----------------------------------------------------------------- Archangelsk
focus('SME_archangelsk_is_ours', 'Archangelsk Is Ours', 36, 6, 35, 'GFX_goal_generic_occupy_states_coastal',
      [['SME_prepare_to_take_back']], 'The White Sea, and a port the Germans never held.',
      owned(214, build('infrastructure', 1)) + '\nadd_stability = 0.05', available='owns_state = 214',
      filt='FOCUS_FILTER_STABILITY')
focus('SME_molotovsk_shipyards', 'The Molotovsk Shipyards', 35, 7, 50, 'GFX_goal_generic_construct_naval_dockyard',
      [['SME_archangelsk_is_ours']], 'Yard No. 402 is finished at last.',
      owned(214, build('dockyard', 3) + '\nadd_building_construction = {\n\ttype = naval_base\n\tlevel = 1\n'
            '\tprovince = { all_provinces = yes limit_to_naval_base = yes }\n\tinstant_build = yes\n}'),
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_pechora_railway', 'The Pechora Railway', 37, 7, 50, 'GFX_goal_generic_construct_infrastructure',
      [['SME_archangelsk_is_ours']], 'The railway to the Vorkuta coal basin.',
      owned(262, build('infrastructure', 2) + '\nadd_resource = {\n\ttype = steel\n\tamount = 15\n}'),
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_white_sea_fleet', 'The White Sea Fleet', 35, 8, 50, 'GFX_goal_generic_build_navy',
      [['SME_molotovsk_shipyards']], 'Ten destroyers and two submarines laid down in Molotovsk.',
      'add_equipment_production = {\n\tequipment = { type = ship_hull_light_1 creator = ROOT }\n\trequested_factories = 1\n\tprogress = 0.25\n\tamount = 10\n}\n'
      'add_equipment_production = {\n\tequipment = { type = ship_hull_submarine_1 creator = ROOT }\n\trequested_factories = 1\n\tprogress = 0.25\n\tamount = 2\n}\n'
      'add_tech_bonus = {\n\tname = SME_white_sea_fleet\n\tbonus = 0.15\n\tuses = 2\n\tcategory = naval_equipment\n}',
      filt='FOCUS_FILTER_NAVY_XP')
focus('SME_northern_sea_route', 'The Northern Sea Route', 36, 9, 50, 'GFX_goal_generic_navy_doctrines_tactics',
      [['SME_pechora_railway'], ['SME_white_sea_fleet']], 'Icebreakers and convoys from the White Sea to the Pacific.',
      'add_equipment_to_stockpile = {\n\ttype = convoy\n\tamount = 20\n\tproducer = ROOT\n}\nadd_ideas = wif_sme_northern_sea_route',
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_window_on_the_west', 'A Window on the West', 36, 10, 35, 'GFX_goal_generic_positive_trade_relations',
      [['SME_northern_sea_route']], 'Ships from America and Britain may call at Archangelsk.',
      'if = {\n\tlimit = { country_exists = USA }\n\tUSA = { add_opinion_modifier = { target = ROOT modifier = medium_increase } }\n}\n'
      'if = {\n\tlimit = { has_idea = wif_sme_northern_sea_route }\n\tswap_ideas = { remove_idea = wif_sme_northern_sea_route add_idea = wif_sme_window_on_the_west }\n}\n'
      'else = {\n\tadd_ideas = wif_sme_window_on_the_west\n}', filt='FOCUS_FILTER_INDUSTRY')

# ----------------------------------------------------------------- Bide Our Time
W = 'FOCUS_FILTER_POLITICAL'
focus('SME_bide_our_time', 'Bide Our Time', 41, 4, 50, 'GFX_goal_generic_neutrality_focus',
      [['SME_prepare_to_take_back']],
      'No war with the Reich until the Reich is at war with itself. The focuses below complete themselves as Germany comes apart.',
      'add_stability = 0.05')
focus('SME_refugees_from_the_east', 'Refugees from the East', 39, 5, 14, 'GFX_goal_generic_allies_build_infantry',
      [['SME_bide_our_time']], 'Germany has bled the East dry, and those who can run are running to us.',
      'add_manpower = 50000\nadd_war_support = 0.05',
      auto='GER = { has_completed_focus = GER_the_east_is_bled_dry }', filt='FOCUS_FILTER_MANPOWER')
focus('SME_the_wehrbauern_arrive', 'The Wehrbauern Arrive', 41, 5, 14, 'GFX_goal_generic_fortify_city',
      [['SME_bide_our_time']], 'Soldier-farmers on the frontier. We dig in opposite them.',
      'add_ideas = wif_sme_wehrbauern_watch', mx=['SME_shovels_instead_of_rifles'],
      auto='GER = { has_completed_focus = GER_wehrbauern }', filt='FOCUS_FILTER_ARMY_XP')
focus('SME_shovels_instead_of_rifles', 'Shovels Instead of Rifles', 43, 5, 14, 'GFX_goal_generic_construction2',
      [['SME_bide_our_time']], 'The frontier divisions are digging, not watching.',
      'add_timed_idea = { idea = wif_sme_shovels_instead_of_rifles days = 730 }', mx=['SME_the_wehrbauern_arrive'],
      auto='GER = { has_completed_focus = GER_labour_battalions }', filt='FOCUS_FILTER_ARMY_XP')
focus('SME_himmler_turns_west', 'Himmler Turns West', 45, 5, 14, 'GFX_goal_generic_intelligence_exchange',
      [['SME_bide_our_time']], 'The SS is looking at Burgundy, not at us.',
      'add_stability = 0.05', auto='GER = { has_completed_focus = GER_offer_retirement }', filt='FOCUS_FILTER_STABILITY')
focus('SME_the_old_man_shakes', 'The Old Man Shakes', 39, 6, 14, 'GFX_goal_generic_political_pressure',
      [['SME_bide_our_time']], 'The newsreels from Berlin have started cutting away early.',
      'add_war_support = 0.05', auto='GER = { has_completed_focus = GER_the_fuhrers_tremor }',
      filt='FOCUS_FILTER_WAR_SUPPORT')
focus('SME_the_reserves_go_home', 'The Reserves Go Home', 41, 6, 14, 'GFX_goal_generic_production',
      [['SME_bide_our_time']], 'The threat on the border is thinning.',
      'add_ideas = wif_sme_reserves_go_home', auto='GER = { has_completed_focus = GER_demobilise_the_reserves }',
      filt='FOCUS_FILTER_INDUSTRY')
focus('SME_two_armies_in_one_reich', 'Two Armies in One Reich', 43, 6, 14, 'GFX_goal_generic_intelligence_exchange',
      [['SME_bide_our_time']], "The Wehrmacht and the SS no longer share codebooks - or secrets.",
      'add_intel = {\n\ttarget = GER\n\tcivilian_intel = 5\n\tarmy_intel = 5\n}',
      auto='GER = { has_completed_focus = GER_two_armies_in_one_reich }')
focus('SME_feed_the_partisans', 'Feed the Partisans', 40, 7, 50, 'GFX_goal_generic_special_forces',
      [['SME_refugees_from_the_east', 'SME_the_old_man_shakes'], ['SME_arm_the_partisans']],
      'Rifles, money and orders for every partisan band between the Urals and the Vistula.',
      'every_state = {\n\tlimit = { is_owned_by = RKM }\n\tadd_compliance = -10\n}\n'
      'every_state = {\n\tlimit = {\n\t\tOR = { is_owned_by = RKM is_owned_by = RKO is_owned_by = RKU is_owned_by = RKK }\n\t}\n\tadd_resistance = 10\n}',
      filt='FOCUS_FILTER_ANNEXATION')
focus('SME_friends_in_the_wehrmacht', 'Friends in the Wehrmacht', 42, 7, 50, 'GFX_goal_generic_dangerous_deal',
      [['SME_himmler_turns_west', 'SME_two_armies_in_one_reich']],
      'There are German officers who would rather talk to us than to Himmler.',
      'add_ideas = wif_sme_friends_in_the_wehrmacht\nadd_war_support = 0.05\n'
      'add_intel = {\n\ttarget = GER\n\tcivilian_intel = 3\n\tarmy_intel = 5\n}\n'
      'if = {\n\tlimit = { country_exists = RKM }\n\tadd_intel = {\n\t\ttarget = RKM\n\t\tcivilian_intel = 5\n\t\tarmy_intel = 5\n\t}\n}')
focus('SME_rifles_from_a_bankrupt_reich', 'Rifles from a Bankrupt Reich', 41, 8, 35, 'GFX_goal_generic_small_arms',
      [['SME_the_reserves_go_home']], 'Bought through Swiss middlemen, no questions asked.',
      'add_equipment_to_stockpile = {\n\ttype = infantry_equipment\n\tamount = 5000\n\tproducer = GER\n}\n'
      'add_equipment_to_stockpile = {\n\ttype = artillery_equipment\n\tamount = 500\n\tproducer = GER\n}',
      available='GER = { has_completed_focus = GER_the_economy_in_free_fall }', filt='FOCUS_FILTER_INDUSTRY')
focus('SME_the_fuhrer_is_dead', 'The Führer Is Dead', 41, 9, 7, 'GFX_goal_generic_occupy_states_ongoing_war',
      [['SME_feed_the_partisans', 'SME_friends_in_the_wehrmacht', 'SME_rifles_from_a_bankrupt_reich']],
      'Berlin has buried him. Now we wait for them to start shooting each other.',
      'add_war_support = 0.10',
      auto='OR = {\n\thas_global_flag = wif_ger_civil_war_begun\n\tAND = {\n\t\tcountry_exists = GER\n'
           '\t\tGER = { has_completed_focus = GER_fuhrer_found_dead }\n\t}\n}',
      filt='FOCUS_FILTER_WAR_SUPPORT')
focus('SME_total_mobilisation', 'Total Mobilisation', 41, 10, 50, 'GFX_goal_generic_axis_build_infantry',
      [['SME_the_fuhrer_is_dead']], 'Every man who can carry a rifle will be needed.',
      'if = {\n\tlimit = { has_idea = volunteer_only }\n\tadd_ideas = limited_conscription\n}\n'
      'else_if = {\n\tlimit = { has_idea = limited_conscription }\n\tadd_ideas = extensive_conscription\n}\n'
      'else_if = {\n\tlimit = { has_idea = extensive_conscription }\n\tadd_ideas = service_by_requirement\n}\n'
      'else_if = {\n\tlimit = { has_idea = service_by_requirement }\n\tadd_ideas = all_adults_serve\n}\n'
      'add_timed_idea = { idea = wif_sme_total_mobilisation days = 730 }', filt='FOCUS_FILTER_MANPOWER')
focus('SME_the_hour_has_come', 'The Hour Has Come', 41, 11, 7, 'GFX_goal_generic_occupy_start_war',
      [['SME_total_mobilisation']], 'The Reich is at war with itself.',
      'add_war_support = 0.15\nadd_stability = 0.10', auto='has_global_flag = wif_ger_civil_war_begun',
      filt='FOCUS_FILTER_WAR_SUPPORT')

IDEAS = {
    'wif_sme_fascist_writers_turned': ('generic_communism_drift_bonus', 'communism_drift = 0.17',
                                       "Fascist Writers, Our Presses", "The fascist papers are shut and their presses print for the Party."),
    'wif_sme_komsomol': ('generic_manpower_bonus', 'conscription = 0.02', 'The Komsomol', 'The Young Communist League recruits in every Ural town.'),
    'wif_sme_heir_to_the_union': ('generic_pp_unity_bonus', 'stability_factor = 0.10\nwar_support_factor = 0.10\nmobilization_laws_cost_factor = -0.10',
                                  'Heir to the Union', 'The Emergency Government has stopped calling itself temporary.'),
    'wif_sme_plan_for_restoration': ('generic_production_bonus', 'production_speed_buildings_factor = 0.10',
                                     'A Plan for Restoration', 'Gosplan, or what is left of it, has a plan.'),
    'wif_sme_ural_industry': ('generic_production_bonus', 'industrial_capacity_factory = 0.05', 'The Ural Workshop',
                              'The Urals build what the Union used to build everywhere.'),
    'wif_sme_ural_industry_2': ('generic_production_bonus', 'industrial_capacity_factory = 0.10', 'The Fourth Five-Year Plan',
                                'The plan Moscow never got to write.'),
    'wif_sme_chelyabinsk_40': ('generic_research_bonus', 'specialization_nuclear_speed_factor = 0.20', 'Chelyabinsk-40',
                               'A closed city behind wire outside Kyshtym.'),
    'wif_sme_deep_battle': ('generic_morale_bonus', 'army_attack_factor = 0.10\narmy_org_factor = 0.10', 'Deep Battle Restored',
                            "Tukhachevsky's doctrine, without Tukhachevsky."),
    'wif_sme_plan_kutuzov': ('generic_war_preparation', 'targeted_modifier = {\n\ttag = RKM\n\tattack_bonus_against = 0.15\n}',
                             'Plan Kutuzov', 'The plan to take back Moscow.'),
    'wif_sme_northern_sea_route': ('generic_sea_focused_navy', 'trade_opinion_factor = 0.10', 'The Northern Sea Route',
                                   'Icebreakers and convoys from the White Sea to the Pacific.'),
    'wif_sme_window_on_the_west': ('generic_foreign_capital', 'trade_opinion_factor = 0.20', 'A Window on the West',
                                   'Ships from America and Britain call at Archangelsk.'),
    'wif_sme_wehrbauern_watch': ('generic_infantry_bonus', 'targeted_modifier = {\n\ttag = RKM\n\tdefense_bonus_against = 0.10\n}\ntargeted_modifier = {\n\ttag = GER\n\tdefense_bonus_against = 0.10\n}',
                                 'Watching the Wehrbauern', 'Soldier-farmers on the frontier, and our divisions dug in opposite them.'),
    'wif_sme_shovels_instead_of_rifles': ('generic_war_preparation', 'targeted_modifier = {\n\ttag = RKM\n\tattack_bonus_against = 0.10\n}',
                                          'Shovels Instead of Rifles', 'The frontier divisions across the border are digging, not watching.'),
    'wif_sme_reserves_go_home': ('generic_production_bonus', 'industrial_capacity_factory = 0.05', 'The Reserves Go Home',
                                 'The threat on the border is thinning, and the factories can work for something other than the next week.'),
    'wif_sme_friends_in_the_wehrmacht': ('generic_spy_intel', 'operative_slot = 1', 'Friends in the Wehrmacht',
                                         'German officers who would rather talk to us than to Himmler.'),
    'wif_sme_total_mobilisation': ('generic_manpower_bonus', 'conscription = 0.05', 'Total Mobilisation',
                                   'Every man who can carry a rifle.'),
}


def gen_focus(f):
    o = ['\tfocus = {', f'\t\tid = {f["id"]}', f'\t\ticon = {f["icon"]}']
    for g in f['pre']:
        o.append('\t\tprerequisite = { ' + ' '.join(f'focus = {x}' for x in g) + ' }')
    if f['mx']:
        o.append('\t\tmutually_exclusive = { ' + ' '.join(f'focus = {x}' for x in f['mx']) + ' }')
    avail = f['available'] or f['auto'] or ''
    if avail:
        o.append(f'\t\tavailable = {{\n{indent(avail, 3)}\n\t\t}}')
    o += [f'\t\tx = {f["x"]}', f'\t\ty = {f["y"]}', f'\t\tcost = {cost(f["days"])}', '',
          f'\t\tsearch_filters = {{ {f["filt"]} }}', '', f'\t\tai_will_do = {{\n\t\t\tfactor = {f["ai"]}\n\t\t}}', '']
    o.append(f'\t\tcompletion_reward = {{\n{indent(f["reward"], 3)}\n\t\t}}')
    o.append('\t}')
    return '\n'.join(o)


def gen_tree():
    path = p('common', 'national_focus', 'SME_focus.txt')
    t = open(path, encoding='utf-8', newline='').read().replace('\r\n', '\n')
    body = ('\t# >>> GENERATED by tools/gen_sme_tree.py - the 1944-1952 continuation from the\n'
            '\t# planner (game x = planner x + 9). Edit the generator, not this block.\n\n' +
            '\n\n'.join(gen_focus(f) for f in F) + '\n\t# <<< GENERATED\n')
    if '# >>> GENERATED' in t:
        t = re.sub(r'\t# >>> GENERATED.*?# <<< GENERATED\n', lambda m: body, t, flags=re.S)
    else:
        i = t.rstrip().rfind('}')
        t = t[:i].rstrip('\n') + '\n\n' + body + '}\n'
    open(path, 'w', encoding='utf-8', newline='').write(t.replace('\n', '\r\n'))


def gen_ideas():
    o = ['# GENERATED by tools/gen_sme_tree.py - spirits of the SME 1944-1952 tree.', 'ideas = {', '\tcountry = {']
    for k, (pic, mod, _, _) in IDEAS.items():
        o += [f'\t\t{k} = {{', '\t\t\tallowed = { always = no }', '\t\t\tallowed_civil_war = { always = yes }',
              '\t\t\tremoval_cost = -1', f'\t\t\tpicture = {pic}', '\t\t\tmodifier = {', indent(mod, 4), '\t\t\t}', '\t\t}']
    o += ['\t}', '}']
    open(p('common', 'ideas', 'wif_sme_tree_ideas.txt'), 'w', encoding='utf-8', newline='').write('\n'.join(o) + '\n')


def gen_watchers():
    o = ['# GENERATED by tools/gen_sme_tree.py.', '#',
         '# SME scope, weekly (on_weekly_SME). Each watcher focus completes itself once',
         '# its prerequisites are done and Germany has done the matching thing. Not',
         '# after the SME has lost its war - the tree is replaced then.', 'wif_sme_tree_watchers = {',
         '\tif = {', '\t\tlimit = { NOT = { has_country_flag = wif_sme_war_lost } }']
    for f in F:
        if not f['auto']:
            continue
        lim = [f'NOT = {{ has_completed_focus = {f["id"]} }}']
        for g in f['pre']:
            lim.append('OR = { ' + ' '.join(f'has_completed_focus = {x}' for x in g) + ' }' if len(g) > 1
                       else f'has_completed_focus = {g[0]}')
        for x in f['mx']:
            lim.append(f'NOT = {{ has_completed_focus = {x} }}')
        if f['auto'].startswith('GER = '):
            lim.append('country_exists = GER')
        lim += f['auto'].split(chr(10))
        o.append('\t\tif = {')
        o.append('\t\t\tlimit = {')
        o += ['\t\t\t\t' + l for l in lim]
        o.append('\t\t\t}')
        o.append(f'\t\t\tcomplete_national_focus = {f["id"]}')
        o.append('\t\t}')
    o += ['\t}', '}']
    open(p('common', 'scripted_effects', 'wif_sme_tree_watchers.txt'), 'w', encoding='utf-8', newline='').write('\n'.join(o) + '\n')


def gen_loc():
    o = ['l_english:']
    for f in F:
        d = f['desc']
        if f['auto']:
            d += '\\n\\n§YCompletes itself§! once Germany gets there.'
        o.append(f' {f["id"]}:0 "{f["name"]}"')
        o.append(f' {f["id"]}_desc:0 "{d}"')
    for k, (_, _, n, d) in IDEAS.items():
        o.append(f' {k}:0 "{n}"')
        o.append(f' {k}_desc:0 "{d}"')
    open(p('localisation', 'english', 'wif_sme_tree_l_english.yml'), 'w', encoding='utf-8-sig', newline='').write('\n'.join(o) + '\n')


def main():
    ids = [f['id'] for f in F]
    assert len(ids) == len(set(ids))
    cells = [(f['x'], f['y']) for f in F]
    assert len(cells) == len(set(cells)), 'overlap'
    gen_tree()
    gen_ideas()
    gen_watchers()
    gen_loc()
    print(len(F), 'focuses')


if __name__ == '__main__':
    main()
