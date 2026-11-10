"""The Cold War "global power" system - source of truth for every wif_gp_* file.

Run:  python tools/gen_global_power.py

Design (agreed with the user 2026-11-10, see the wif-global-power-system memory):
  * Tiers, ranked monthly by a power score:
        4 Global Power (max 4, max 2 per faction, needs nukes + the advanced
          large airframe, never a subject)
        3 Growing Superpower (max 3, needs nukes, must LEAD its own faction,
          cannot be influenced)
        2 Great Power   1 Regional Power   0 Minor
    Puppets top out at Regional Power. Enter a top tier after 3 months as a
    candidate, leave after 6 months out (losing eligibility is instant).
  * Global Powers get a rival (ideology matrix), credibility (0-100, both
    reputation and currency), up to 5 claimed regions and the Weltpolitik
    decision menu: influence campaigns drift ideology, flip governments and
    pull countries into the bloc. Two different ideologies pushing on one
    country can start a civil war; an AI patron always sends a volunteer
    corps, a human patron is asked.
  * Proxy wars: Regional Powers and Minors only, started only by event.
    Nobody else may join (on_war_relation_added makes them white-peace out).
    Patrons can widen, halt (occupation line becomes the border), split the
    loser in two, or escalate into a full bloc war.
  * Nuclear doctrine (shown in the Nuclear Command menu, changed only by
    script): Last Resort / Threat Launch / First Strike / Purifying Flame.
    AI launches are scripted; a strike kills 8% of the state, destroys a
    rocket-site level and grounds the state's air base while fallout lasts.
  * Sphere cohesion -> strain / crisis (defections, domino) / collapse.
  * Non-Aligned Movement and the prestige races.

Writes (all GENERATED - edit this file, not them):
  common/scripted_triggers/wif_gp_triggers.txt
  common/scripted_effects/wif_gp_effects.txt
  common/scripted_effects/wif_gp_regions_auto.txt
  common/on_actions/wif_gp_on_actions.txt
  common/decisions/wif_gp_decisions.txt
  common/decisions/categories/wif_gp_categories.txt
  common/ideas/wif_gp_ideas.txt
  common/dynamic_modifiers/wif_gp_dynamic_modifiers.txt
  common/opinion_modifiers/wif_gp_opinion_modifiers.txt
  common/ai_strategy/wif_gp_ai.txt
  common/scripted_localisation/wif_gp_scripted_loc.txt
  common/special_projects/projects/nuclear_projects.txt  (vanilla copy + AI weights)
  common/special_projects/projects/rocket_projects.txt   (vanilla copy + AI weights)
  events/wif_gp_events.txt
  localisation/english/wif_gp_l_english.yml

The two special-project files are COPIES of vanilla with one AI modifier added
to seven projects. Re-run this generator after a game update.
"""
import os
import re

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GAME = r"C:/Program Files (x86)/Steam/steamapps/common/Hearts of Iron IV"

SLOTS = [1, 2, 3, 4]
IDEOLOGIES = ['democratic', 'fascism', 'communism', 'neutrality']

# ---------------------------------------------------------------------------
# Tuning
# ---------------------------------------------------------------------------
GREAT_MIN, GREAT_FRAC = 150, 0.25      # Great Power: score >= max(150, 25% of the top)
REGIONAL_MIN, REGIONAL_FRAC = 40, 0.06
NUKE_CAP = 60                          # nukes beyond 60 add nothing to the score
MAX_CLAIMS = 5
CLAIM_PP, CLAIM_CRED = 150, 15
FALLOUT_DAYS = 180
MAX_PROXY_WARS = 3

# Rival weights: chooser ideology -> candidate ideology -> weight
RIVAL_MATRIX = {
    'democratic': {'communism': 60, 'fascism': 60, 'democratic': 5, 'neutrality': 15},
    'fascism':    {'communism': 80, 'democratic': 40, 'fascism': 10, 'neutrality': 15},
    'communism':  {'fascism': 60, 'democratic': 60, 'communism': 2, 'neutrality': 15},
    'neutrality': {'communism': 25, 'fascism': 25, 'democratic': 25, 'neutrality': 25},
}

# Claimable regions: key, display name, strategic region ids (land and the
# sea regions that hold island states).
REGIONS = [
    ('western_europe', 'Western Europe', [1, 2, 3, 4, 5, 19, 20, 208, 41, 209, 210, 23, 16, 29, 47, 51, 68, 169]),
    ('central_europe', 'Central Europe', [6, 7, 8, 21, 22, 38, 39]),
    ('nordic', 'Scandinavia', [10, 11, 191, 192, 276, 13, 277, 278, 275, 161, 45, 206]),
    ('balkans', 'the Balkans', [24, 25, 26, 27, 202]),
    ('eastern_europe', 'Eastern Europe', [37, 130, 131, 132, 133, 134, 135, 40, 138, 150, 264, 265, 12]),
    ('middle_east', 'the Middle East', [129, 28, 232, 196, 236, 237, 238, 116, 239, 240, 241, 297, 298, 69]),
    ('north_africa', 'North Africa', [126, 182, 225, 128, 127]),
    ('africa', 'Sub-Saharan Africa', [17, 139, 140, 183, 184, 185, 216, 217, 223, 224, 226, 227, 271, 272, 273, 274, 181, 48, 60, 61, 62, 85, 102]),
    ('south_asia', 'South Asia', [31, 141, 153, 190, 230, 231, 253, 254, 290, 291, 296, 162, 289, 146, 71, 99, 101]),
    ('central_asia', 'Central Asia', [136, 137, 267, 268, 269, 270]),
    ('siberia', 'Siberia', [14, 147, 148, 149, 151, 255, 256, 257, 258, 259, 260, 261, 262, 263, 266, 88]),
    ('east_asia', 'East Asia', [143, 144, 145, 164, 165, 200, 244, 245, 246, 247, 248, 249, 250, 251, 152, 155, 242, 243, 186, 154, 299, 300, 252, 76, 87]),
    ('southeast_asia', 'South-East Asia', [142, 228, 229, 292, 293, 294, 295, 188, 187, 158, 159, 160, 167, 189, 78, 91, 93]),
    ('oceania', 'Oceania and the Pacific', [156, 157, 193, 194, 195, 301, 302, 303, 304, 32, 83, 84, 94, 95, 97, 105, 172, 178, 179, 180]),
    ('north_america', 'North America', [33, 117, 118, 119, 120, 121, 122, 166, 197, 198, 199, 211, 212, 213, 214, 215, 218, 219, 220, 221, 222, 233, 234, 235, 36, 57, 170]),
    ('latin_america', 'Central America and the Caribbean', [34, 123, 204, 205, 53, 52]),
    ('south_america', 'South America', [35, 124, 125, 163, 201, 280, 281, 282, 283, 284, 285, 286, 287, 288, 64, 109]),
]

# Prestige races: key, display, trigger (country scope)
RACES = [
    ('atomic', 'the Atomic Bomb', 'has_tech = nukes'),
    ('thermo', 'the Hydrogen Bomb', 'has_tech = thermonuclear_bombs'),
    ('icbm', 'the Intercontinental Ballistic Missile', 'is_special_project_completed = sp:sp_rockets_long_range_ballistic_missile'),
    ('bomber', 'the Intercontinental Bomber', 'is_special_project_completed = sp:sp_air_intercontinental_bomber'),
    ('jet', 'the Jet Engine', 'is_special_project_completed = sp:sp_air_jet_engine'),
    ('nucsub', 'the Nuclear Submarine', 'is_special_project_completed = sp:sp_naval_nuclear_submarine'),
]

# Special projects the Nuclear Ambition flag pushes the AI towards.
SP_PUSH = {
    'nuclear_projects.txt': ['sp_nuclear_reactor', 'sp_nuclear_bomb', 'sp_thermo_nuclear_bomb', 'sp_nuclear_warheads'],
    'rocket_projects.txt': ['sp_rockets_ballistic_missile', 'sp_rockets_medium_range_ballistic_missile',
                            'sp_rockets_long_range_ballistic_missile'],
}

IMMUNE_IDEAS = ['wif_cw_no_diplomatic_standing', 'wif_splinter_no_factions']


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def write(rel, text, bom=False):
    """4-space indentation in the templates becomes tabs; CRLF; BOM for .yml."""
    out = []
    for line in text.split('\n'):
        stripped = line.lstrip(' ')
        n = len(line) - len(stripped)
        out.append('\t' * (n // 4) + ' ' * (n % 4) + stripped)
    text = '\r\n'.join(out)
    path = os.path.join(MOD, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8-sig' if bom else 'utf-8', newline='') as f:
        f.write(text)
    print('wrote', rel)


def sub(text, **kw):
    for k, v in kw.items():
        text = text.replace('@' + k + '@', str(v))
    return text


def indent(text, n):
    pad = '    ' * n
    return '\n'.join(pad + l if l.strip() else l for l in text.split('\n'))


HEADER = '# GENERATED by tools/gen_global_power.py - edit the generator, not this file.\n\n'


# ---------------------------------------------------------------------------
# Map: state -> region
# ---------------------------------------------------------------------------
def merged_files(sub_dir):
    files = {}
    for root in (GAME, MOD):
        d = os.path.join(root, sub_dir)
        if os.path.isdir(d):
            for f in os.listdir(d):
                if f.endswith('.txt'):
                    files[f] = os.path.join(d, f)
    return sorted(files.values())


def read(path):
    with open(path, encoding='utf-8-sig', errors='replace') as fh:
        return re.sub(r'#[^\n]*', '', fh.read())


def provinces_block(text):
    m = re.search(r'\bprovinces\s*=\s*\{([^}]*)\}', text)
    return [int(x) for x in m.group(1).split()] if m else []


def state_regions():
    prov_sr = {}
    for path in merged_files('map/strategicregions'):
        text = read(path)
        rid = int(re.search(r'\bid\s*=\s*(\d+)', text).group(1))
        for p in provinces_block(text):
            prov_sr[p] = rid
    sr_region = {}
    for i, (_k, _n, srs) in enumerate(REGIONS, 1):
        for s in srs:
            assert s not in sr_region, f'strategic region {s} listed twice'
            sr_region[s] = i
    result, unmapped = {}, {}
    for path in merged_files('history/states'):
        text = read(path)
        m = re.search(r'\bstate\s*=\s*\{', text)
        if not m:
            continue
        sid = int(re.search(r'\bid\s*=\s*(\d+)', text[m.end():]).group(1))
        votes = {}
        for p in provinces_block(text[m.end():]):
            r = prov_sr.get(p)
            if r is not None:
                votes[r] = votes.get(r, 0) + 1
        if not votes:
            continue
        sr = max(votes, key=votes.get)
        if sr in sr_region:
            result[sid] = sr_region[sr]
        else:
            unmapped.setdefault(sr, []).append(sid)
    if unmapped:
        print('WARNING: states in strategic regions mapped to no geo-region:', unmapped)
    return result


# ---------------------------------------------------------------------------
# Scripted triggers
# ---------------------------------------------------------------------------
def gen_triggers():
    t = HEADER
    t += '# "No Diplomatic Standing" - both spirits that carry that name.\n'
    t += 'wif_gp_immune_spirit = {\n    OR = {\n'
    t += ''.join(f'        has_idea = {i}\n' for i in IMMUNE_IDEAS)
    t += '    }\n}\n\n'
    t += '''wif_gp_is_global = { check_variable = { wif_gp_tier = 4 } }
wif_gp_is_growing = { check_variable = { wif_gp_tier = 3 } }
# Regional Power or Minor - the only sizes allowed to fight proxy wars.
wif_gp_is_proxy_size = { NOT = { check_variable = { wif_gp_tier > 1 } } }

# Global Powers, Growing Superpowers and No Diplomatic Standing are immune.
wif_gp_cannot_be_influenced = {
    OR = {
        wif_gp_immune_spirit = yes
        check_variable = { wif_gp_tier > 2 }
    }
}

wif_gp_eligible_global = {
    exists = yes
    is_subject = no
    has_capitulated = no
    has_tech = nukes
    has_tech = advanced_large_airframe
    wif_gp_immune_spirit = no
}

wif_gp_eligible_growing = {
    exists = yes
    is_subject = no
    has_capitulated = no
    has_tech = nukes
    is_faction_leader = yes
    wif_gp_immune_spirit = no
}

wif_gp_nuclear_power = {
    OR = {
        has_tech = nukes
        num_of_nukes > 0
    }
}

# A delivery system that is not sitting under fallout: a big air base plus a
# heavy airframe, or a rocket site plus a ballistic missile.
wif_gp_can_deliver = {
    OR = {
        AND = {
            OR = {
                has_tech = basic_large_airframe
                has_tech = improved_large_airframe
                has_tech = advanced_large_airframe
            }
            any_controlled_state = {
                air_base > 2
                NOT = { has_state_flag = wif_gp_fallout }
            }
        }
        AND = {
            OR = {
                is_special_project_completed = sp:sp_rockets_medium_range_ballistic_missile
                is_special_project_completed = sp:sp_rockets_long_range_ballistic_missile
            }
            any_controlled_state = {
                rocket_site > 0
                NOT = { has_state_flag = wif_gp_fallout }
            }
        }
    }
}

# The faction of THIS has fewer than two Global Power picks this month.
wif_gp_faction_has_room = {
    OR = {
        is_in_faction = no
        NOT = {
            any_country = {
                is_faction_leader = yes
                OR = {
                    tag = PREV
                    is_in_faction_with = PREV
                }
                check_variable = { wif_gp_fac_picks > 1 }
            }
        }
    }
}

wif_gp_nam_member = { has_idea = wif_gp_nam_member_idea }

wif_gp_nam_eligible = {
    exists = yes
    has_global_flag = wif_gp_atomic_age
    is_subject = no
    is_in_faction = no
    has_capitulated = no
    wif_gp_immune_spirit = no
    check_variable = { wif_gp_tier > 0 }
    check_variable = { wif_gp_tier < 3 }
    wif_gp_nam_member = no
'''
    for s in SLOTS:
        t += f'    NOT = {{ check_variable = {{ wif_gp_inf_{s} > 39 }} }}\n'
    t += '}\n\n'

    # Slot helpers
    for s in SLOTS:
        t += f'# --- slot {s} ---\n'
        t += sub('''wif_gp_slot_@S@_used = { has_global_flag = wif_gp_slot_@S@_used }
# THIS has the same government as the slot-@S@ Global Power.
wif_gp_same_gov_as_slot_@S@ = {
    has_global_flag = wif_gp_slot_@S@_used
    OR = {
''', S=s)
        for i in IDEOLOGIES:
            t += f'        AND = {{ has_government = {i} var:global.wif_gp_slot_{s} = {{ has_government = {i} }} }}\n'
        t += '    }\n}\n'
        t += f'# The slot-{s} ideology is above 30% in THIS.\nwif_gp_slot_{s}_pop_over_30 = {{\n    OR = {{\n'
        for i in IDEOLOGIES:
            t += f'        AND = {{ {i} > 0.3 var:global.wif_gp_slot_{s} = {{ has_government = {i} }} }}\n'
        t += '    }\n}\n'
        t += f'wif_gp_slot_{s}_pop_over_45 = {{\n    OR = {{\n'
        for i in IDEOLOGIES:
            t += f'        AND = {{ {i} > 0.45 var:global.wif_gp_slot_{s} = {{ has_government = {i} }} }}\n'
        t += '    }\n}\n'
        # Join-ready for slot s (target scope)
        t += sub('''wif_gp_join_ready_@S@ = {
    has_global_flag = wif_gp_slot_@S@_used
    check_variable = { wif_gp_inf_@S@ > 59 }
    wif_gp_same_gov_as_slot_@S@ = yes
    is_in_faction = no
    is_subject = no
    has_war = no
}
''', S=s)
        t += '\n'

    # Two slots have different governments
    for a in SLOTS:
        for b in SLOTS:
            if a < b:
                t += f'wif_gp_slots_{a}_{b}_differ = {{\n    has_global_flag = wif_gp_slot_{a}_used\n    has_global_flag = wif_gp_slot_{b}_used\n    NOT = {{\n        OR = {{\n'
                for i in IDEOLOGIES:
                    t += f'            AND = {{ var:global.wif_gp_slot_{a} = {{ has_government = {i} }} var:global.wif_gp_slot_{b} = {{ has_government = {i} }} }}\n'
                t += '        }\n    }\n}\n'
    t += '\n'

    # Regions
    for i, (k, _n, _s) in enumerate(REGIONS, 1):
        t += f'wif_gp_capital_in_{k} = {{ capital_scope = {{ check_variable = {{ wif_gp_region = {i} }} }} }}\n'
    t += '\n# ROOT-scope decision helper: FROM\'s capital lies in a region ROOT claims.\n'
    t += 'wif_gp_from_in_root_claims = {\n    OR = {\n'
    for k, _n, _s in REGIONS:
        t += f'        AND = {{ has_country_flag = wif_gp_claim_{k} FROM = {{ wif_gp_capital_in_{k} = yes }} }}\n'
    t += '    }\n}\n\n'

    # Influence campaign targets (FROM = target, ROOT = Global)
    t += '''# FROM may be targeted by ROOT's influence decisions.
wif_gp_valid_influence_target = {
    FROM = {
        exists = yes
        NOT = { tag = ROOT }
        is_subject = no
        wif_gp_cannot_be_influenced = no
        NOT = { is_subject_of = ROOT }
    }
    wif_gp_from_in_root_claims = yes
}

# ROOT is FROM's patron (subject, faction leader or client).
wif_gp_root_is_from_patron = {
    FROM = {
        has_country_flag = wif_gp_has_patron
        var:wif_gp_patron = { tag = ROOT }
    }
}

'''
    for s in SLOTS:
        t += sub('''# ROOT (slot @S@) has FROM's patron as its rival.
wif_gp_from_in_rival_sphere_@S@ = {
    FROM = {
        has_country_flag = wif_gp_has_patron
        wif_gp_cannot_be_influenced = no
        var:wif_gp_patron = { has_country_flag = wif_gp_rival_of_@S@ }
    }
}
''', S=s)
    t += '''
# Proxy wars ----------------------------------------------------------------
wif_gp_in_proxy = { check_variable = { wif_gp_px_id > 0 } }

# State scope: owned by a member of the winning side of proxy war cur_id.
wif_gp_on_win_side = {
    check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
    check_variable = { wif_gp_px_side = global.wif_gp_win_side }
}

# State scope: a frontier state for border-first picking.
wif_gp_bfs_frontier = {
    NOT = { has_state_flag = wif_gp_bfs }
    OR = {
        controller = { wif_gp_on_win_side = yes }
        any_neighbor_state = { has_state_flag = wif_gp_bfs }
        any_neighbor_state = { controller = { wif_gp_on_win_side = yes } }
        any_neighbor_state = { owner = { wif_gp_on_win_side = yes } }
    }
}

# Nuclear targets (state scope, ROOT = the nuking country) -------------------
wif_gp_nt_enemy = {
    controller = { has_war_with = ROOT }
    owner = { has_war_with = ROOT }
}
wif_gp_nt_mad = {
    wif_gp_nt_enemy = yes
    controller = { has_country_flag = wif_gp_mad_target_tmp }
}
wif_gp_nt_silo = {
    wif_gp_nt_enemy = yes
    NOT = { has_state_flag = wif_gp_fallout }
    rocket_site > 0
}
wif_gp_nt_airbase = {
    wif_gp_nt_enemy = yes
    NOT = { has_state_flag = wif_gp_fallout }
    air_base > 2
}
wif_gp_nt_industry = {
    wif_gp_nt_enemy = yes
    NOT = { has_state_flag = wif_gp_fallout }
    OR = {
        arms_factory > 2
        industrial_complex > 3
        dockyard > 2
    }
}
wif_gp_nt_city = {
    wif_gp_nt_enemy = yes
    OR = {
        is_capital = yes
        state_population_k > 1500
    }
}
wif_gp_nt_anything = {
    wif_gp_nt_enemy = yes
    OR = {
        is_capital = yes
        state_population_k > 500
        supply_node > 0
        rocket_site > 0
        air_base > 0
        arms_factory > 0
        industrial_complex > 0
    }
}
'''
    return t


# ---------------------------------------------------------------------------
# Scripted effects
# ---------------------------------------------------------------------------
def gen_region_effects(regions):
    t = HEADER
    t += '# Tags every state with the geo-region its capital decides influence by.\n'
    t += 'wif_gp_init_regions = {\n'
    by_region = {}
    for sid, r in sorted(regions.items()):
        by_region.setdefault(r, []).append(sid)
    for r in sorted(by_region):
        t += f'    # {REGIONS[r - 1][1]}\n'
        for sid in by_region[r]:
            t += f'    {sid} = {{ set_variable = {{ wif_gp_region = {r} }} }}\n'
    t += '    set_global_flag = wif_gp_regions_done\n}\n'
    return t


def slot_ideology_branch(s, body_by_ideology):
    """body_by_ideology(i) -> effect text run if the slot power has ideology i."""
    t = ''
    first = True
    for i in IDEOLOGIES:
        kw = 'if' if first else 'else_if'
        first = False
        t += f'{kw} = {{\n    limit = {{ var:global.wif_gp_slot_{s} = {{ has_government = {i} }} }}\n'
        t += indent(body_by_ideology(i), 1) + '\n}\n'
    return t


def gen_effects():
    t = HEADER

    # ------------------------------------------------------------------ score
    t += sub('''# ===========================================================================
# POWER SCORE (country scope)
# ===========================================================================
wif_gp_calc_score = {
    set_temp_variable = { s = num_of_military_factories }
    multiply_temp_variable = { s = 3 }
    set_temp_variable = { t = num_of_civilian_factories }
    multiply_temp_variable = { t = 2 }
    add_to_temp_variable = { s = t }
    set_temp_variable = { t = num_of_naval_factories }
    multiply_temp_variable = { t = 2 }
    add_to_temp_variable = { s = t }
    set_temp_variable = { t = num_divisions }
    clamp_temp_variable = { var = t min = 0 max = 200 }
    add_to_temp_variable = { s = t }
    set_temp_variable = { t = num_of_nukes }
    clamp_temp_variable = { var = t min = 0 max = @NC@ }
    multiply_temp_variable = { t = 5 }
    add_to_temp_variable = { s = t }
    set_variable = { wif_gp_subf = 0 }
    every_subject_country = {
        add_to_variable = { PREV.wif_gp_subf = num_of_factories }
    }
    multiply_variable = { wif_gp_subf = 0.5 }
    add_to_temp_variable = { s = wif_gp_subf }
    if = { limit = { has_tech = nukes } add_to_temp_variable = { s = 50 } }
    if = { limit = { has_tech = thermonuclear_bombs } add_to_temp_variable = { s = 50 } }
    if = { limit = { has_tech = advanced_large_airframe } add_to_temp_variable = { s = 20 } }
    if = {
        limit = { is_special_project_completed = sp:sp_rockets_long_range_ballistic_missile }
        add_to_temp_variable = { s = 50 }
    }
    # Space race and other milestones (tools/gen_space_race.py).
    add_to_temp_variable = { s = wif_gp_bonus_score }

    # Low stability: up to -30%. Surrender progress: up to -50%. Lost capital: -25%.
    set_temp_variable = { m = 1 }
    if = {
        limit = { has_stability < 0.5 }
        set_temp_variable = { k = stability }
        multiply_temp_variable = { k = 0.6 }
        add_to_temp_variable = { k = 0.7 }
        multiply_temp_variable = { m = k }
    }
    set_temp_variable = { k = surrender_progress }
    multiply_temp_variable = { k = -0.5 }
    add_to_temp_variable = { k = 1 }
    multiply_temp_variable = { m = k }
    if = {
        limit = { capital_scope = { NOT = { is_controlled_by = PREV } } }
        multiply_temp_variable = { m = 0.75 }
    }
    multiply_temp_variable = { s = m }
    set_variable = { wif_gp_score = s }
}

''', NC=NUKE_CAP)

    # ------------------------------------------------------------- ranking
    t += '''# ===========================================================================
# MONTHLY GLOBAL PASS - run once a month from whichever country's on_monthly
# arrives first (see the lock in wif_gp_on_actions.txt).
# ===========================================================================
wif_gp_monthly = {
    if = { limit = { NOT = { has_global_flag = wif_gp_regions_done } } wif_gp_init_regions = yes }
    wif_gp_rank_countries = yes
    wif_gp_update_patrons = yes
    wif_gp_influence_tick = yes
    wif_gp_civil_war_sponsors = yes
    wif_gp_global_upkeep = yes
    wif_gp_defend_checks = yes
    wif_gp_proxy_war_spawn = yes
    wif_gp_nam_upkeep = yes
    wif_gp_prestige_races = yes
    wif_gp_proliferation = yes
}

wif_gp_rank_countries = {
    set_variable = { global.wif_gp_top = 1 }
    every_country = {
        wif_gp_calc_score = yes
        if = {
            limit = { check_variable = { wif_gp_score > global.wif_gp_top } }
            set_variable = { global.wif_gp_top = wif_gp_score }
        }
        clr_country_flag = wif_gp_pick
        clr_country_flag = wif_gp_gpick
        clr_country_flag = wif_gp_overshadow_now
        set_variable = { wif_gp_fac_picks = 0 }
    }
    set_variable = { global.wif_gp_great_min = global.wif_gp_top }
    multiply_variable = { global.wif_gp_great_min = ''' + str(GREAT_FRAC) + ''' }
    if = {
        limit = { check_variable = { global.wif_gp_great_min < ''' + str(GREAT_MIN) + ''' } }
        set_variable = { global.wif_gp_great_min = ''' + str(GREAT_MIN) + ''' }
    }
    set_variable = { global.wif_gp_reg_min = global.wif_gp_top }
    multiply_variable = { global.wif_gp_reg_min = ''' + str(REGIONAL_FRAC) + ''' }
    if = {
        limit = { check_variable = { global.wif_gp_reg_min < ''' + str(REGIONAL_MIN) + ''' } }
        set_variable = { global.wif_gp_reg_min = ''' + str(REGIONAL_MIN) + ''' }
    }

    # Four rounds: the strongest eligible country whose faction has room.
'''
    for _ in range(4):
        t += '''    set_variable = { global.wif_gp_best_score = 0 }
    every_country = {
        limit = {
            wif_gp_eligible_global = yes
            NOT = { has_country_flag = wif_gp_pick }
            wif_gp_faction_has_room = yes
        }
        if = {
            limit = { check_variable = { wif_gp_score > global.wif_gp_best_score } }
            set_variable = { global.wif_gp_best_score = wif_gp_score }
            set_variable = { global.wif_gp_best = THIS }
            set_global_flag = wif_gp_best_found
        }
    }
    if = {
        limit = { has_global_flag = wif_gp_best_found }
        clr_global_flag = wif_gp_best_found
        var:global.wif_gp_best = {
            set_country_flag = wif_gp_pick
            if = {
                limit = { is_in_faction = yes }
                random_country = {
                    limit = {
                        is_faction_leader = yes
                        OR = {
                            tag = PREV
                            is_in_faction_with = PREV
                        }
                    }
                    add_to_variable = { wif_gp_fac_picks = 1 }
                }
            }
        }
    }
'''
    t += '''
    # Eligible, but two stronger Global Powers already stand in its faction.
    every_country = {
        limit = {
            wif_gp_eligible_global = yes
            NOT = { has_country_flag = wif_gp_pick }
            wif_gp_faction_has_room = no
        }
        set_country_flag = wif_gp_overshadow_now
    }

    # Global Power hysteresis: 3 months in, 6 months out, instant on losing
    # eligibility or being overshadowed.
    every_country = {
        if = {
            limit = { has_country_flag = wif_gp_pick }
            add_to_variable = { wif_gp_cand_months = 1 }
        }
        else = { set_variable = { wif_gp_cand_months = 0 } }
        if = {
            limit = { wif_gp_is_global = yes }
            if = {
                limit = { has_country_flag = wif_gp_pick }
                set_variable = { wif_gp_out_months = 0 }
            }
            else = { add_to_variable = { wif_gp_out_months = 1 } }
            if = {
                limit = { has_country_flag = wif_gp_overshadow_now }
                set_country_flag = wif_gp_overshadowed
                wif_gp_demote_global = yes
            }
            else_if = {
                limit = {
                    OR = {
                        wif_gp_eligible_global = no
                        check_variable = { wif_gp_out_months > 5 }
                    }
                }
                wif_gp_demote_global = yes
            }
        }
    }
    every_country = {
        limit = {
            NOT = { wif_gp_is_global = yes }
            has_country_flag = wif_gp_pick
            check_variable = { wif_gp_cand_months > 2 }
            check_variable = { global.wif_gp_global_count < 4 }
        }
        wif_gp_promote_global = yes
    }

    # Growing Superpowers: three rounds over the eligible non-Globals.
'''
    for _ in range(3):
        t += '''    set_variable = { global.wif_gp_best_score = 0 }
    every_country = {
        limit = {
            wif_gp_eligible_growing = yes
            NOT = { wif_gp_is_global = yes }
            NOT = { has_country_flag = wif_gp_gpick }
        }
        if = {
            limit = { check_variable = { wif_gp_score > global.wif_gp_best_score } }
            set_variable = { global.wif_gp_best_score = wif_gp_score }
            set_variable = { global.wif_gp_best = THIS }
            set_global_flag = wif_gp_best_found
        }
    }
    if = {
        limit = { has_global_flag = wif_gp_best_found }
        clr_global_flag = wif_gp_best_found
        var:global.wif_gp_best = { set_country_flag = wif_gp_gpick }
    }
'''
    t += '''    every_country = {
        if = {
            limit = { has_country_flag = wif_gp_gpick }
            add_to_variable = { wif_gp_gcand_months = 1 }
        }
        else = { set_variable = { wif_gp_gcand_months = 0 } }
        if = {
            limit = { has_country_flag = wif_gp_growing }
            if = {
                limit = { has_country_flag = wif_gp_gpick }
                set_variable = { wif_gp_gout_months = 0 }
            }
            else = { add_to_variable = { wif_gp_gout_months = 1 } }
            if = {
                limit = {
                    OR = {
                        wif_gp_is_global = yes
                        wif_gp_eligible_growing = no
                        check_variable = { wif_gp_gout_months > 5 }
                    }
                }
                clr_country_flag = wif_gp_growing
                subtract_from_variable = { global.wif_gp_growing_count = 1 }
                log = "WiF GP: [This.GetName] is no longer a Growing Superpower"
            }
        }
    }
    every_country = {
        limit = {
            NOT = { has_country_flag = wif_gp_growing }
            NOT = { wif_gp_is_global = yes }
            has_country_flag = wif_gp_gpick
            check_variable = { wif_gp_gcand_months > 2 }
            check_variable = { global.wif_gp_growing_count < 3 }
        }
        set_country_flag = wif_gp_growing
        add_to_variable = { global.wif_gp_growing_count = 1 }
        set_variable = { wif_gp_gout_months = 0 }
        country_event = { id = wif_gp.7 }
        log = "WiF GP: [This.GetName] became a Growing Superpower"
    }

    # Everyone's tier and spirit.
    every_country = {
        if = {
            limit = { wif_gp_is_global = yes }
        }
        else_if = {
            limit = { has_country_flag = wif_gp_growing }
            set_variable = { wif_gp_tier = 3 }
        }
        else_if = {
            limit = {
                is_subject = no
                NOT = { check_variable = { wif_gp_score < global.wif_gp_great_min } }
            }
            set_variable = { wif_gp_tier = 2 }
        }
        else_if = {
            limit = { NOT = { check_variable = { wif_gp_score < global.wif_gp_reg_min } } }
            set_variable = { wif_gp_tier = 1 }
        }
        else = { set_variable = { wif_gp_tier = 0 } }
        wif_gp_apply_tier_idea = yes

        # Overshadowed lasts while the reason does.
        if = {
            limit = {
                has_country_flag = wif_gp_overshadowed
                NOT = { has_country_flag = wif_gp_overshadow_now }
            }
            clr_country_flag = wif_gp_overshadowed
        }
        if = {
            limit = { has_country_flag = wif_gp_overshadowed NOT = { has_idea = wif_gp_overshadowed_idea } }
            add_ideas = wif_gp_overshadowed_idea
        }
        else_if = {
            limit = { NOT = { has_country_flag = wif_gp_overshadowed } has_idea = wif_gp_overshadowed_idea }
            remove_ideas = wif_gp_overshadowed_idea
        }

        # Nuclear Ambition: once the Atomic Age has begun, every Great Power and
        # up chases the bomb, the bomber and the missile.
        if = {
            limit = {
                has_global_flag = wif_gp_atomic_age
                check_variable = { wif_gp_tier > 1 }
            }
            set_country_flag = wif_gp_nuclear_ambition
        }
        else = { clr_country_flag = wif_gp_nuclear_ambition }
    }
}

wif_gp_apply_tier_idea = {
'''
    names = {4: 'wif_gp_tier_global', 3: 'wif_gp_tier_growing', 2: 'wif_gp_tier_great', 1: 'wif_gp_tier_regional'}
    for n, idea in names.items():
        t += f'''    if = {{
        limit = {{ check_variable = {{ wif_gp_tier = {n} }} NOT = {{ has_idea = {idea} }} }}
        add_ideas = {idea}
    }}
    else_if = {{
        limit = {{ NOT = {{ check_variable = {{ wif_gp_tier = {n} }} }} has_idea = {idea} }}
        remove_ideas = {idea}
    }}
'''
    t += '}\n\n'

    # promote / demote
    t += '''# THIS becomes a Global Power and takes the first free slot.
wif_gp_promote_global = {
'''
    first = True
    for s in SLOTS:
        kw = 'if' if first else 'else_if'
        first = False
        t += f'''    {kw} = {{
        limit = {{ NOT = {{ has_global_flag = wif_gp_slot_{s}_used }} }}
        set_global_flag = wif_gp_slot_{s}_used
        set_variable = {{ global.wif_gp_slot_{s} = THIS }}
        set_variable = {{ wif_gp_slot = {s} }}
    }}
'''
    t += '''    set_variable = { wif_gp_tier = 4 }
    add_to_variable = { global.wif_gp_global_count = 1 }
    set_variable = { wif_gp_out_months = 0 }
    set_variable = { wif_gp_cred = 50 }
    set_variable = { wif_gp_cohesion = 60 }
    set_variable = { wif_gp_claims = 0 }
    set_variable = { wif_gp_cg = 0 }
    clr_country_flag = wif_gp_strain
    clr_country_flag = wif_gp_crisis
    clr_country_flag = wif_gp_overshadowed
    if = {
        limit = { has_country_flag = wif_gp_growing }
        clr_country_flag = wif_gp_growing
        subtract_from_variable = { global.wif_gp_growing_count = 1 }
    }
    if = {
        limit = { NOT = { has_dynamic_modifier = { modifier = wif_gp_commitments } } }
        add_dynamic_modifier = { modifier = wif_gp_commitments }
    }
    wif_gp_apply_tier_idea = yes
    if = {
        limit = { NOT = { has_global_flag = wif_gp_atomic_age } }
        set_global_flag = wif_gp_atomic_age
        news_event = { id = wif_gp.1 days = 1 }
    }
    else = {
        news_event = { id = wif_gp.2 days = 1 }
    }
    wif_gp_choose_rival = yes
    log = "WiF GP: [This.GetName] became a Global Power (score [?This.wif_gp_score])"
}

# THIS stops being a Global Power. wif_gp_overshadowed set = faction rule.
wif_gp_demote_global = {
'''
    for s in SLOTS:
        t += f'''    if = {{
        limit = {{ check_variable = {{ wif_gp_slot = {s} }} }}
        clr_global_flag = wif_gp_slot_{s}_used
        clear_variable = global.wif_gp_slot_{s}
        every_country = {{
            set_variable = {{ wif_gp_inf_{s} = 0 }}
            set_variable = {{ wif_gp_fav_{s} = 0 }}
            clr_country_flag = wif_gp_camp_{s}
            clr_country_flag = wif_gp_rival_of_{s}
        }}
    }}
'''
    for k, _n, _s in REGIONS:
        t += f'    clr_country_flag = wif_gp_claim_{k}\n'
    t += '''    set_variable = { wif_gp_slot = 0 }
    set_variable = { wif_gp_claims = 0 }
    set_variable = { wif_gp_tier = 2 }
    subtract_from_variable = { global.wif_gp_global_count = 1 }
    set_variable = { wif_gp_cand_months = 0 }
    clr_country_flag = wif_gp_strain
    clr_country_flag = wif_gp_crisis
    clear_variable = wif_gp_rival
    if = {
        limit = { has_dynamic_modifier = { modifier = wif_gp_commitments } }
        remove_dynamic_modifier = { modifier = wif_gp_commitments }
    }
    wif_gp_apply_tier_idea = yes
    if = {
        limit = { has_country_flag = wif_gp_overshadowed }
        country_event = { id = wif_gp.5 }
    }
    else_if = {
        limit = { exists = yes }
        news_event = { id = wif_gp.4 days = 1 }
        country_event = { id = wif_gp.3 days = 2 }
    }
    log = "WiF GP: [This.GetName] is no longer a Global Power"
}

'''

    # ------------------------------------------------------------- rival
    t += '''# ===========================================================================
# RIVAL (Global Power scope). Pool: other Global Powers, else Growing
# Superpowers, else Great Powers. Never a faction mate or a subject.
# ===========================================================================
wif_gp_choose_rival = {
    set_variable = { wif_gp_pool = 2 }
    if = {
        limit = {
            any_country = {
                NOT = { tag = PREV }
                check_variable = { wif_gp_tier = 3 }
                NOT = { is_in_faction_with = PREV }
            }
        }
        set_variable = { wif_gp_pool = 3 }
    }
    if = {
        limit = {
            any_country = {
                NOT = { tag = PREV }
                check_variable = { wif_gp_tier = 4 }
                NOT = { is_in_faction_with = PREV }
            }
        }
        set_variable = { wif_gp_pool = 4 }
    }
    set_variable = { wif_gp_rw_best = 0 }
    clr_country_flag = wif_gp_rival_found
    every_country = {
        limit = {
            NOT = { tag = PREV }
            is_subject = no
            NOT = { is_in_faction_with = PREV }
            check_variable = { wif_gp_tier = PREV.wif_gp_pool }
        }
        set_variable = { wif_gp_rw = 25 }
'''
    first = True
    for ci, row in RIVAL_MATRIX.items():
        for ti, w in row.items():
            kw = 'if' if first else 'else_if'
            first = False
            t += f'''        {kw} = {{
            limit = {{ PREV = {{ has_government = {ci} }} has_government = {ti} }}
            set_variable = {{ wif_gp_rw = {w} }}
        }}
'''
    t += '''        if = { limit = { is_neighbor_of = PREV } add_to_variable = { wif_gp_rw = 20 } }
        set_temp_variable = { strong = global.wif_gp_top }
        multiply_temp_variable = { strong = 0.9 }
        if = { limit = { check_variable = { wif_gp_score > strong } } add_to_variable = { wif_gp_rw = 15 } }
        if = { limit = { has_country_flag = wif_gp_current_rival_tmp } add_to_variable = { wif_gp_rw = 25 } }
        if = {
            limit = { check_variable = { wif_gp_rw > PREV.wif_gp_rw_best } }
            PREV = {
                set_variable = { wif_gp_rw_best = PREV.wif_gp_rw }
                set_variable = { wif_gp_rival_new = PREV }
                set_country_flag = wif_gp_rival_found
            }
        }
    }
    if = {
        limit = { has_country_flag = wif_gp_rival_found }
        clr_country_flag = wif_gp_rival_found
        # The AI antagonises its rival - once per rival, removed on a change.
        if = {
            limit = { has_variable = wif_gp_rival }
            var:wif_gp_rival = {
                if = {
                    limit = { PREV = { is_ai = yes has_country_flag = wif_gp_ai_rival_set } }
                    PREV = { add_ai_strategy = { type = antagonize id = PREV value = -60 } }
                }
            }
        }
        set_variable = { wif_gp_rival = wif_gp_rival_new }
        var:wif_gp_rival = {
            PREV = {
                if = {
                    limit = { is_ai = yes }
                    add_ai_strategy = { type = antagonize id = PREV value = 60 }
                    set_country_flag = wif_gp_ai_rival_set
                }
            }
        }
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ check_variable = {{ wif_gp_slot = {s} }} }}
            every_country = {{ clr_country_flag = wif_gp_rival_of_{s} }}
            var:wif_gp_rival = {{ set_country_flag = wif_gp_rival_of_{s} }}
        }}
'''
    t += '''        if = {
            limit = {
                has_government = communism
                var:wif_gp_rival = { has_government = communism }
                NOT = { has_global_flag = wif_gp_sino_soviet_split }
            }
            set_global_flag = wif_gp_sino_soviet_split
            news_event = { id = wif_gp.6 days = 1 }
        }
        country_event = { id = wif_gp.10 days = 1 }
        log = "WiF GP: [This.GetName] chose [?This.wif_gp_rival.GetName] as its rival"
    }
}

'''

    # ------------------------------------------------------------- patrons
    t += '''# ===========================================================================
# PATRONS: subject > faction member of a Global Power leader > client (60+
# influence). Losing a member costs the old patron credibility.
# ===========================================================================
wif_gp_update_patrons = {
    every_country = {
        if = {
            limit = { has_country_flag = wif_gp_has_patron }
            set_variable = { wif_gp_prev_patron = wif_gp_patron }
            set_country_flag = wif_gp_had_patron
        }
        else = { clr_country_flag = wif_gp_had_patron }
        clr_country_flag = wif_gp_has_patron
        clear_variable = wif_gp_patron
    }
'''
    for s in SLOTS:
        t += f'''    if = {{
        limit = {{ has_global_flag = wif_gp_slot_{s}_used }}
        var:global.wif_gp_slot_{s} = {{
            every_subject_country = {{
                limit = {{ NOT = {{ has_country_flag = wif_gp_has_patron }} }}
                set_variable = {{ wif_gp_patron = PREV }}
                set_country_flag = wif_gp_has_patron
            }}
            if = {{
                limit = {{ is_faction_leader = yes }}
                every_country = {{
                    limit = {{
                        is_in_faction_with = PREV
                        NOT = {{ tag = PREV }}
                        NOT = {{ has_country_flag = wif_gp_has_patron }}
                        NOT = {{ check_variable = {{ wif_gp_tier > 2 }} }}
                    }}
                    set_variable = {{ wif_gp_patron = PREV }}
                    set_country_flag = wif_gp_has_patron
                }}
            }}
        }}
        every_country = {{
            limit = {{
                NOT = {{ has_country_flag = wif_gp_has_patron }}
                check_variable = {{ wif_gp_inf_{s} > 59 }}
                wif_gp_cannot_be_influenced = no
            }}
            set_variable = {{ wif_gp_patron = global.wif_gp_slot_{s} }}
            set_country_flag = wif_gp_has_patron
        }}
    }}
'''
    t += '''    # Lost members: the old patron, if still a Global Power, pays for it.
    every_country = {
        limit = {
            has_country_flag = wif_gp_had_patron
            NOT = { has_country_flag = wif_gp_defected }
            OR = {
                NOT = { has_country_flag = wif_gp_has_patron }
                NOT = { check_variable = { wif_gp_patron = wif_gp_prev_patron } }
            }
        }
        var:wif_gp_prev_patron = {
            if = {
                limit = { exists = yes wif_gp_is_global = yes }
                add_to_variable = { wif_gp_cred = -8 }
                clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
                set_variable = { wif_gp_ev_target = PREV }
                if = { limit = { is_ai = no } country_event = { id = wif_gp.46 } }
            }
        }
    }
}

'''

    # ------------------------------------------------------------- influence tick
    t += '''# ===========================================================================
# INFLUENCE (monthly, target scope)
# ===========================================================================
wif_gp_influence_tick = {
    every_country = {
        limit = {
            wif_gp_cannot_be_influenced = no
            OR = {
'''
    for s in SLOTS:
        t += f'                has_country_flag = wif_gp_camp_{s}\n'
        t += f'                check_variable = {{ wif_gp_inf_{s} > 0 }}\n'
    t += '''            }
        }
'''
    for s in SLOTS:
        body = sub('''if = {
    limit = { has_global_flag = wif_gp_slot_@S@_used }
    if = {
        limit = { has_country_flag = wif_gp_camp_@S@ }
        set_temp_variable = { g = 4 }
        if = { limit = { wif_gp_nam_member = yes } multiply_temp_variable = { g = 0.5 } }
        if = { limit = { check_variable = { wif_gp_tier = 2 } } multiply_temp_variable = { g = 0.5 } }
        if = { limit = { wif_gp_same_gov_as_slot_@S@ = yes } multiply_temp_variable = { g = 1.25 } }
        # A rival's sphere in crisis is cheap to work on.
        if = {
            limit = {
                has_country_flag = wif_gp_has_patron
                NOT = { check_variable = { wif_gp_patron = global.wif_gp_slot_@S@ } }
                var:wif_gp_patron = { has_country_flag = wif_gp_crisis }
            }
            multiply_temp_variable = { g = 2 }
        }
        add_to_variable = { wif_gp_inf_@S@ = g }
        add_to_variable = { wif_gp_fav_@S@ = 1 }
    }
    # Decay: faster in the Non-Aligned Movement and for a patron in crisis.
    set_temp_variable = { dc = 1 }
    if = { limit = { wif_gp_nam_member = yes } set_temp_variable = { dc = 2 } }
    if = {
        limit = { var:global.wif_gp_slot_@S@ = { has_country_flag = wif_gp_crisis } }
        add_to_temp_variable = { dc = 2 }
    }
    subtract_from_variable = { wif_gp_inf_@S@ = dc }
    subtract_from_variable = { wif_gp_fav_@S@ = 0.5 }
    clamp_variable = { var = wif_gp_inf_@S@ min = 0 max = 100 }
    clamp_variable = { var = wif_gp_fav_@S@ min = 0 max = 100 }

    # Ideology drift.
    if = {
        limit = { check_variable = { wif_gp_inf_@S@ > 9 } }
        set_temp_variable = { dp = 0.01 }
        if = { limit = { check_variable = { wif_gp_inf_@S@ > 29 } } set_temp_variable = { dp = 0.02 } }
        if = { limit = { check_variable = { wif_gp_inf_@S@ > 59 } } set_temp_variable = { dp = 0.03 } }
''', S=s)
        body += indent(slot_ideology_branch(s, lambda i: f'add_popularity = {{ ideology = {i} popularity = dp }}'), 2) + '\n'
        body += sub('''    }

    # Government change at 40+ once the ideology leads (AI targets flip, a
    # human target is asked at most every 180 days).
    if = {
        limit = {
            check_variable = { wif_gp_inf_@S@ > 39 }
            wif_gp_same_gov_as_slot_@S@ = no
            wif_gp_slot_@S@_pop_over_45 = yes
            has_war = no
            has_civil_war = no
        }
        if = {
            limit = { is_ai = yes }
''', S=s)
        body += indent(slot_ideology_branch(s, lambda i: f'set_politics = {{ ruling_party = {i} elections_allowed = {"yes" if i == "democratic" else "no"} }}'), 3) + '\n'
        body += sub('''            var:global.wif_gp_slot_@S@ = { add_to_variable = { wif_gp_cred = 2 } }
            log = "WiF GP: [This.GetName] changed government under slot-@S@ influence"
        }
        else_if = {
            limit = { NOT = { has_country_flag = wif_gp_gov_offer_cd } }
            set_country_flag = { flag = wif_gp_gov_offer_cd value = 1 days = 180 }
            set_variable = { wif_gp_ev_power = global.wif_gp_slot_@S@ }
            set_variable = { wif_gp_ev_slot = @S@ }
            country_event = { id = wif_gp.20 }
        }
    }
}
''', S=s)
        t += indent(body, 2) + '\n'

    # Joining - highest favour among join-ready slots wins
    for s in SLOTS:
        cond = f'wif_gp_join_ready_{s} = yes\n'
        for o in SLOTS:
            if o != s:
                cond += (f'NOT = {{ AND = {{ wif_gp_join_ready_{o} = yes '
                         f'check_variable = {{ wif_gp_fav_{o} > wif_gp_fav_{s} }} }} }}\n')
        body = f'''if = {{
    limit = {{
{indent(cond.rstrip(), 2)}
    }}
    if = {{
        limit = {{ is_ai = yes }}
        wif_gp_join_slot_{s} = yes
    }}
    else_if = {{
        limit = {{ NOT = {{ has_country_flag = wif_gp_join_offer_cd }} }}
        set_country_flag = {{ flag = wif_gp_join_offer_cd value = 1 days = 180 }}
        set_variable = {{ wif_gp_ev_power = global.wif_gp_slot_{s} }}
        set_variable = {{ wif_gp_ev_slot = {s} }}
        country_event = {{ id = wif_gp.21 }}
    }}
}}
'''
        t += indent(body, 2) + '\n'

    # Contest -> civil war
    pairs = [(a, b) for a in SLOTS for b in SLOTS if a < b]
    for a, b in pairs:
        body = sub('''# Contest between slot @A@ and slot @B@.
if = {
    limit = {
        wif_gp_slots_@A@_@B@_differ = yes
        check_variable = { wif_gp_inf_@A@ > 24 }
        check_variable = { wif_gp_inf_@B@ > 24 }
        wif_gp_slot_@A@_pop_over_30 = yes
        wif_gp_slot_@B@_pop_over_30 = yes
        has_war = no
        has_civil_war = no
        NOT = { has_country_flag = wif_gp_cw_cd }
    }
    random_list = {
        10 = {
            set_country_flag = { flag = wif_gp_cw_cd value = 1 days = 730 }
            if = {
                limit = { wif_gp_same_gov_as_slot_@A@ = yes }
                wif_gp_civil_war_for_slot_@B@ = yes
            }
            else_if = {
                limit = { wif_gp_same_gov_as_slot_@B@ = yes }
                wif_gp_civil_war_for_slot_@A@ = yes
            }
            else_if = {
                limit = { check_variable = { wif_gp_inf_@A@ > wif_gp_inf_@B@ } }
                wif_gp_set_gov_slot_@A@ = yes
                wif_gp_civil_war_for_slot_@B@ = yes
            }
            else = {
                wif_gp_set_gov_slot_@B@ = yes
                wif_gp_civil_war_for_slot_@A@ = yes
            }
        }
        90 = { }
    }
}
''', A=a, B=b)
        t += indent(body, 2) + '\n'
    t += '    }\n}\n\n'

    for s in SLOTS:
        t += f'wif_gp_civil_war_for_slot_{s} = {{\n'
        t += indent(slot_ideology_branch(s, lambda i: f'start_civil_war = {{ ideology = {i} size = 0.5 }}'), 1) + '\n'
        t += f'    log = "WiF GP: contested influence threw [This.GetName] into civil war (slot {s} revolts)"\n}}\n'
        t += f'wif_gp_set_gov_slot_{s} = {{\n'
        t += indent(slot_ideology_branch(s, lambda i: f'set_politics = {{ ruling_party = {i} elections_allowed = {"yes" if i == "democratic" else "no"} }}'), 1) + '\n}\n'
        t += sub('''# THIS joins the slot-@S@ bloc (creating a faction if needed).
wif_gp_join_slot_@S@ = {
    set_country_flag = wif_gp_joining
    if = {
        limit = { wif_gp_nam_member = yes }
        remove_ideas = wif_gp_nam_member_idea
    }
    var:global.wif_gp_slot_@S@ = {
        if = {
            limit = { is_in_faction = no }
            create_faction = wif_gp_bloc_faction
        }
        if = {
            limit = { is_faction_leader = yes }
            every_country = {
                limit = { has_country_flag = wif_gp_joining }
                PREV = { add_to_faction = PREV }
            }
        }
        else = {
            random_country = {
                limit = {
                    is_faction_leader = yes
                    is_in_faction_with = PREV
                }
                every_country = {
                    limit = { has_country_flag = wif_gp_joining }
                    PREV = { add_to_faction = PREV }
                }
            }
        }
        add_to_variable = { wif_gp_cred = 5 }
        clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
    }
    clr_country_flag = wif_gp_joining
    log = "WiF GP: [This.GetName] joined the bloc of slot @S@"
}

''', S=s)

    # ------------------------------------------------------------- civil war sponsors
    t += '''# ===========================================================================
# CIVIL WARS: every Global Power with influence backs the side of its own
# ideology. AI patrons always send a corps; a human patron is asked. Two
# different patrons on opposite sides of a small country = a proxy war.
# ===========================================================================
wif_gp_civil_war_sponsors = {
    every_country = {
        limit = {
            has_country_flag = wif_gp_cw_handled
            has_civil_war = no
        }
        clr_country_flag = wif_gp_cw_handled
    }
    every_country = {
        limit = {
            has_civil_war = yes
            NOT = { has_country_flag = wif_gp_cw_handled }
            wif_gp_cannot_be_influenced = no
            any_country = {
                civilwar_target = PREV
                has_war_with = PREV
            }
        }
        set_country_flag = wif_gp_cw_handled
        random_country = {
            limit = {
                civilwar_target = PREV
                has_war_with = PREV
            }
            set_country_flag = wif_gp_cw_handled
            set_country_flag = wif_gp_cw_rebel_tmp
            clear_variable = wif_gp_cw_patron
        }
        clear_variable = wif_gp_cw_patron
'''
    for s in SLOTS:
        t += sub('''        if = {
            limit = {
                has_global_flag = wif_gp_slot_@S@_used
                check_variable = { wif_gp_inf_@S@ > 9 }
            }
            # Which side shares the patron's government?
            if = {
                limit = { wif_gp_same_gov_as_slot_@S@ = yes }
                set_variable = { wif_gp_cw_patron = global.wif_gp_slot_@S@ }
                wif_gp_sponsor_side = yes
            }
            random_country = {
                limit = {
                    has_country_flag = wif_gp_cw_rebel_tmp
                    wif_gp_same_gov_as_slot_@S@ = yes
                }
                set_variable = { wif_gp_inf_@S@ = PREV.wif_gp_inf_@S@ }
                set_variable = { wif_gp_cw_patron = global.wif_gp_slot_@S@ }
                wif_gp_sponsor_side = yes
            }
        }
''', S=s)
    t += '''        # Two different patrons on opposite sides of a small country.
        if = {
            limit = {
                wif_gp_is_proxy_size = yes
                has_variable = wif_gp_cw_patron
                any_country = {
                    has_country_flag = wif_gp_cw_rebel_tmp
                    has_variable = wif_gp_cw_patron
                    NOT = { check_variable = { wif_gp_cw_patron = PREV.wif_gp_cw_patron } }
                }
            }
            add_to_variable = { global.wif_gp_px_next = 1 }
            set_variable = { wif_gp_px_id = global.wif_gp_px_next }
            set_variable = { wif_gp_px_side = 1 }
            set_variable = { wif_gp_px_patron = wif_gp_cw_patron }
            set_country_flag = wif_gp_px_main
            set_country_flag = wif_gp_px_civil
            random_country = {
                limit = { has_country_flag = wif_gp_cw_rebel_tmp }
                set_variable = { wif_gp_px_id = global.wif_gp_px_next }
                set_variable = { wif_gp_px_side = 2 }
                set_variable = { wif_gp_px_patron = wif_gp_cw_patron }
                set_country_flag = wif_gp_px_main
                set_country_flag = wif_gp_px_civil
            }
            add_to_variable = { global.wif_gp_px_count = 1 }
            news_event = { id = wif_gp.51 days = 1 }
        }
        every_country = {
            limit = { has_country_flag = wif_gp_cw_rebel_tmp }
            clr_country_flag = wif_gp_cw_rebel_tmp
        }
    }
}

# THIS is a civil-war side; wif_gp_cw_patron is its patron.
wif_gp_sponsor_side = {
    set_variable = { wif_gp_vol_from = wif_gp_cw_patron }
    var:wif_gp_cw_patron = {
        if = {
            limit = { is_ai = yes }
            PREV = { country_event = { id = wif_gp.27 } }
        }
        else = {
            set_variable = { wif_gp_ev_target = PREV }
            country_event = { id = wif_gp.26 }
        }
    }
}

'''

    # ------------------------------------------------------------- upkeep: cred, cohesion, claims, overstretch
    t += '''# ===========================================================================
# GLOBAL POWER UPKEEP: credibility drift, cohesion, crisis, claim capacity,
# arms race, overstretched economy, Test of Resolve, yearly rival check.
# ===========================================================================
wif_gp_global_upkeep = {
    # Reset the per-member loyalty used by the defection checks.
    every_country = { set_variable = { wif_gp_loyalty = 50 } }
'''
    for s in SLOTS:
        t += sub('''    if = {
        limit = { has_global_flag = wif_gp_slot_@S@_used }
        var:global.wif_gp_slot_@S@ = {
            set_variable = { wif_gp_coh_n = 0 }
            set_variable = { wif_gp_coh_sum = 0 }
        }
        every_country = {
            limit = {
                has_country_flag = wif_gp_has_patron
                check_variable = { wif_gp_patron = global.wif_gp_slot_@S@ }
            }
            set_temp_variable = { l = 50 }
            if = {
                limit = { check_variable = { wif_gp_inf_@S@ > 50 } }
                set_temp_variable = { l = wif_gp_inf_@S@ }
            }
            add_to_temp_variable = { l = wif_gp_fav_@S@ }
            multiply_temp_variable = { l = 0.85 }
            if = { limit = { wif_gp_same_gov_as_slot_@S@ = no } subtract_from_temp_variable = { l = 15 } }
            if = { limit = { has_country_flag = wif_gp_secession } subtract_from_temp_variable = { l = 20 } }
            if = { limit = { has_country_flag = wif_gp_resentment } subtract_from_temp_variable = { l = 10 } }
            if = { limit = { has_country_flag = wif_gp_subsidised } add_to_temp_variable = { l = 15 } }
''', S=s)
        for o in SLOTS:
            if o != s:
                t += f'            if = {{ limit = {{ check_variable = {{ wif_gp_inf_{o} > 29 }} }} subtract_from_temp_variable = {{ l = 15 }} }}\n'
        t += sub('''            clamp_temp_variable = { var = l min = 0 max = 100 }
            set_variable = { wif_gp_loyalty = l }
            var:global.wif_gp_slot_@S@ = {
                add_to_variable = { wif_gp_coh_n = 1 }
                add_to_variable = { wif_gp_coh_sum = PREV.wif_gp_loyalty }
            }
        }
        var:global.wif_gp_slot_@S@ = { wif_gp_upkeep_self = yes }
        if = {
            limit = { has_global_flag = wif_gp_slot_@S@_used }
            wif_gp_defections_slot_@S@ = yes
        }
    }
''', S=s)
    t += '}\n\n'

    t += '''# Global Power scope.
wif_gp_upkeep_self = {
    # Credibility drifts back towards 50.
    if = { limit = { check_variable = { wif_gp_cred > 51 } } add_to_variable = { wif_gp_cred = -1 } }
    else_if = { limit = { check_variable = { wif_gp_cred < 49 } } add_to_variable = { wif_gp_cred = 1 } }
    clamp_variable = { var = wif_gp_cred min = 0 max = 100 }

    # Claim capacity: what the AI thinks it can carry.
    set_variable = { wif_gp_claim_cap = 2 }
    set_temp_variable = { half = global.wif_gp_top }
    multiply_temp_variable = { half = 0.5 }
    if = { limit = { check_variable = { wif_gp_score > half } } add_to_variable = { wif_gp_claim_cap = 1 } }
    multiply_temp_variable = { half = 1.8 }
    if = { limit = { check_variable = { wif_gp_score > half } } add_to_variable = { wif_gp_claim_cap = 1 } }
    if = { limit = { check_variable = { wif_gp_cred > 69 } } add_to_variable = { wif_gp_claim_cap = 1 } }
    if = { limit = { check_variable = { wif_gp_cohesion < 50 } } add_to_variable = { wif_gp_claim_cap = -1 } }
    clamp_variable = { var = wif_gp_claim_cap min = 1 max = ''' + str(MAX_CLAIMS) + ''' }
    set_variable = { wif_gp_claim_cap_gamble = wif_gp_claim_cap }
    add_to_variable = { wif_gp_claim_cap_gamble = 1 }

    # Global Commitments: 2% consumer goods per claimed region.
    set_variable = { wif_gp_cg = wif_gp_claims }
    multiply_variable = { wif_gp_cg = 0.02 }

    # Cohesion target = (average member loyalty + credibility) / 2, minus
    # domestic trouble; it moves at most 5 points a month.
    set_temp_variable = { tgt = wif_gp_cred }
    if = {
        limit = { check_variable = { wif_gp_coh_n > 0 } }
        set_temp_variable = { avg = wif_gp_coh_sum }
        divide_temp_variable = { avg = wif_gp_coh_n }
        add_to_temp_variable = { tgt = avg }
        divide_temp_variable = { tgt = 2 }
    }
    if = { limit = { has_stability < 0.3 } subtract_from_temp_variable = { tgt = 15 } }
    if = { limit = { surrender_progress > 0.2 } subtract_from_temp_variable = { tgt = 20 } }
    if = { limit = { capital_scope = { NOT = { is_controlled_by = PREV } } } subtract_from_temp_variable = { tgt = 15 } }
    if = { limit = { has_idea = wif_gp_overstretched_idea } subtract_from_temp_variable = { tgt = 10 } }
    set_temp_variable = { over = wif_gp_claims }
    subtract_from_temp_variable = { over = wif_gp_claim_cap }
    if = {
        limit = { check_temp_variable = { over > 0 } }
        multiply_temp_variable = { over = 10 }
        subtract_from_temp_variable = { tgt = over }
    }
    if = { limit = { has_country_flag = wif_gp_reformed } add_to_temp_variable = { tgt = 25 } }
    set_temp_variable = { d = tgt }
    subtract_from_temp_variable = { d = wif_gp_cohesion }
    clamp_temp_variable = { var = d min = -5 max = 5 }
    add_to_variable = { wif_gp_cohesion = d }
    clamp_variable = { var = wif_gp_cohesion min = 0 max = 100 }

    # Stages.
    if = {
        limit = { check_variable = { wif_gp_cohesion < 10 } }
        log = "WiF GP: [This.GetName]'s sphere has collapsed"
        news_event = { id = wif_gp.43 days = 1 }
        every_country = {
            limit = { is_subject_of = PREV }
            random_list = {
                25 = { PREV = { end_puppet = PREV } }
                75 = { }
            }
        }
        wif_gp_demote_global = yes
    }
    else_if = {
        limit = { check_variable = { wif_gp_cohesion < 30 } NOT = { has_country_flag = wif_gp_crisis } }
        set_country_flag = wif_gp_crisis
        set_country_flag = wif_gp_strain
        news_event = { id = wif_gp.41 days = 1 }
    }
    else_if = {
        limit = { check_variable = { wif_gp_cohesion < 50 } NOT = { has_country_flag = wif_gp_strain } }
        set_country_flag = wif_gp_strain
        country_event = { id = wif_gp.40 }
    }
    else_if = {
        limit = {
            check_variable = { wif_gp_cohesion > 54 }
            has_country_flag = wif_gp_strain
        }
        if = {
            limit = { has_country_flag = wif_gp_crisis }
            add_to_variable = { wif_gp_cred = 10 }
            add_timed_idea = { idea = wif_gp_sphere_holds_idea days = 180 }
            country_event = { id = wif_gp.42 }
        }
        clr_country_flag = wif_gp_strain
        clr_country_flag = wif_gp_crisis
    }

    # Arms race: the rival out-builds us.
    clr_country_flag = wif_gp_arms_race
    if = {
        limit = { has_variable = wif_gp_rival }
        var:wif_gp_rival = { set_variable = { PREV.wif_gp_rival_mil = num_of_military_factories } }
        if = {
            limit = { check_variable = { wif_gp_rival_mil > num_of_military_factories } }
            set_country_flag = wif_gp_arms_race
        }
    }

    # Overstretched Economy: military factories above 1.5x civilian for 24 months.
    set_temp_variable = { civ = num_of_civilian_factories }
    multiply_temp_variable = { civ = 1.5 }
    set_temp_variable = { mil = num_of_military_factories }
    if = {
        limit = { check_temp_variable = { mil > civ } }
        add_to_variable = { wif_gp_overstretch_months = 1 }
    }
    else = { set_variable = { wif_gp_overstretch_months = 0 } }
    if = {
        limit = {
            check_variable = { wif_gp_overstretch_months > 23 }
            NOT = { has_idea = wif_gp_overstretched_idea }
        }
        add_ideas = wif_gp_overstretched_idea
        country_event = { id = wif_gp.90 }
    }
    else_if = {
        limit = {
            has_idea = wif_gp_overstretched_idea
            check_variable = { wif_gp_overstretch_months = 0 }
        }
        remove_ideas = wif_gp_overstretched_idea
    }

    # Yearly rival check (or if the rival is gone or no longer a peer).
    add_to_variable = { wif_gp_rival_months = 1 }
    if = {
        limit = {
            OR = {
                check_variable = { wif_gp_rival_months > 11 }
                NOT = { has_variable = wif_gp_rival }
                var:wif_gp_rival = {
                    OR = {
                        exists = no
                        is_subject = yes
                        check_variable = { wif_gp_tier < 2 }
                    }
                }
            }
        }
        set_variable = { wif_gp_rival_months = 0 }
        if = {
            limit = { has_variable = wif_gp_rival }
            var:wif_gp_rival = { set_country_flag = wif_gp_current_rival_tmp }
        }
        wif_gp_choose_rival = yes
        every_country = {
            limit = { has_country_flag = wif_gp_current_rival_tmp }
            clr_country_flag = wif_gp_current_rival_tmp
        }
    }

    # Test of Resolve: the rival probes one of our smaller sphere members.
    set_country_flag = wif_gp_tor_self
    if = {
        limit = {
            has_variable = wif_gp_rival
            var:wif_gp_rival = { is_ai = yes wif_gp_is_global = yes }
            NOT = { has_country_flag = wif_gp_tor_cd }
            any_country = {
                has_country_flag = wif_gp_has_patron
                var:wif_gp_patron = { has_country_flag = wif_gp_tor_self }
                wif_gp_is_proxy_size = yes
            }
        }
        random_list = {
            3 = {
                set_country_flag = { flag = wif_gp_tor_cd value = 1 days = 365 }
                set_variable = { wif_gp_ev_power = wif_gp_rival }
                random_country = {
                    limit = {
                        has_country_flag = wif_gp_has_patron
                        wif_gp_is_proxy_size = yes
                        var:wif_gp_patron = { has_country_flag = wif_gp_tor_self }
                    }
                    PREV = { set_variable = { wif_gp_ev_target = PREV } }
                }
                country_event = { id = wif_gp.31 }
            }
            97 = { }
        }
    }
    clr_country_flag = wif_gp_tor_self
}

'''
    # defections per slot
    for s in SLOTS:
        t += sub('''# Crisis defections for slot @S@ (target-side checks).
wif_gp_defections_slot_@S@ = {
    if = {
        limit = { var:global.wif_gp_slot_@S@ = { has_country_flag = wif_gp_crisis } }
        every_country = {
            limit = {
                has_country_flag = wif_gp_has_patron
                check_variable = { wif_gp_patron = global.wif_gp_slot_@S@ }
                check_variable = { wif_gp_loyalty < 30 }
            }
            set_temp_variable = { ch = 10 }
            if = { limit = { var:global.wif_gp_slot_@S@ = { check_variable = { wif_gp_cohesion < 20 } } } set_temp_variable = { ch = 20 } }
            if = { limit = { var:global.wif_gp_slot_@S@ = { has_country_flag = wif_gp_retreat_shield } } multiply_temp_variable = { ch = 0.5 } }
            if = { limit = { has_country_flag = wif_gp_secession } multiply_temp_variable = { ch = 2 } }
            randomize_temp_variable = roll
            multiply_temp_variable = { roll = 100 }
            if = {
                limit = { check_temp_variable = { roll < ch } }
                wif_gp_defect_from_slot_@S@ = yes
            }
        }
    }
}

wif_gp_defect_from_slot_@S@ = {
    if = {
        limit = { var:global.wif_gp_slot_@S@ = { has_subject = PREV } }
        var:global.wif_gp_slot_@S@ = { end_puppet = PREV }
    }
    else_if = {
        limit = { var:global.wif_gp_slot_@S@ = { is_in_faction_with = PREV } }
        leave_faction = yes
    }
    else = {
        set_variable = { wif_gp_inf_@S@ = 20 }
    }
    set_country_flag = { flag = wif_gp_defected value = 1 days = 365 }
    var:global.wif_gp_slot_@S@ = {
        if = {
            limit = { has_country_flag = wif_gp_retreat_shield }
            add_to_variable = { wif_gp_cred = -5 }
        }
        else = { add_to_variable = { wif_gp_cred = -10 } }
        clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
    }
    log = "WiF GP: [This.GetName] defected from the slot-@S@ sphere"
}

''', S=s)

    # ------------------------------------------------------------- defend checks
    t += '''# ===========================================================================
# CREDIBILITY: was an attacked sphere member defended within 60 days?
# ===========================================================================
wif_gp_defend_checks = {
    every_country = {
        limit = { has_country_flag = wif_gp_defend_pending }
        if = {
            limit = { has_country_flag = wif_gp_has_patron }
            var:wif_gp_patron = { set_country_flag = wif_gp_tmp_pat }
        }
        if = {
            limit = {
                OR = {
                    has_country_flag = wif_gp_supported
                    AND = {
                        has_variable = wif_gp_attacker
                        var:wif_gp_attacker = {
                            any_country = {
                                has_country_flag = wif_gp_tmp_pat
                                has_war_with = PREV
                            }
                        }
                    }
                }
            }
            clr_country_flag = wif_gp_defend_pending
            if = {
                limit = { has_country_flag = wif_gp_has_patron }
                var:wif_gp_patron = {
                    add_to_variable = { wif_gp_cred = 10 }
                    clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
                }
            }
        }
        else_if = {
            limit = { NOT = { has_country_flag = wif_gp_defend_window } }
            clr_country_flag = wif_gp_defend_pending
            if = {
                limit = { has_country_flag = wif_gp_has_patron }
                var:wif_gp_patron = {
                    add_to_variable = { wif_gp_cred = -15 }
                    clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
                }
            }
        }
        every_country = {
            limit = { has_country_flag = wif_gp_tmp_pat }
            clr_country_flag = wif_gp_tmp_pat
        }
    }
}

'''

    # ------------------------------------------------------------- proxy wars
    t += '''# ===========================================================================
# PROXY WARS
# ===========================================================================
# Monthly: maybe a border clash between two small clients of different blocs.
wif_gp_proxy_war_spawn = {
    if = {
        limit = {
            NOT = { has_global_flag = wif_gp_px_cooldown }
            check_variable = { global.wif_gp_px_count < ''' + str(MAX_PROXY_WARS) + ''' }
            check_variable = { global.wif_gp_global_count > 1 }
        }
        every_country = {
            limit = {
                NOT = { has_global_flag = wif_gp_px_cooldown }
                wif_gp_is_proxy_size = yes
                has_country_flag = wif_gp_has_patron
                has_war = no
                has_capitulated = no
                wif_gp_immune_spirit = no
            }
            var:wif_gp_patron = { set_country_flag = wif_gp_tmp_aggpat }
            if = {
                limit = {
                    any_neighbor_country = {
                        wif_gp_is_proxy_size = yes
                        has_country_flag = wif_gp_has_patron
                        has_war = no
                        has_capitulated = no
                        wif_gp_immune_spirit = no
                        var:wif_gp_patron = {
                            NOT = { has_country_flag = wif_gp_tmp_aggpat }
                            NOT = {
                                any_country = {
                                    has_country_flag = wif_gp_tmp_aggpat
                                    is_in_faction_with = PREV
                                }
                            }
                        }
                    }
                }
                set_temp_variable = { ch = 1 }
                if = { limit = { has_country_flag = wif_gp_border_tension } set_temp_variable = { ch = 6 } }
                randomize_temp_variable = roll
                multiply_temp_variable = { roll = 100 }
                if = {
                    limit = {
                        check_temp_variable = { roll < ch }
                        NOT = { has_global_flag = wif_gp_px_cooldown }
                    }
                    random_neighbor_country = {
                        limit = {
                            wif_gp_is_proxy_size = yes
                            has_country_flag = wif_gp_has_patron
                            has_war = no
                            has_capitulated = no
                            wif_gp_immune_spirit = no
                            var:wif_gp_patron = {
                                NOT = { has_country_flag = wif_gp_tmp_aggpat }
                                NOT = {
                                    any_country = {
                                        has_country_flag = wif_gp_tmp_aggpat
                                        is_in_faction_with = PREV
                                    }
                                }
                            }
                        }
                        PREV = {
                            set_variable = { wif_gp_ev_target = PREV }
                            set_variable = { wif_gp_ev_tscore = PREV.wif_gp_score }
                        }
                    }
                    set_global_flag = { flag = wif_gp_px_cooldown value = 1 days = 180 }
                    country_event = { id = wif_gp.50 }
                }
            }
            every_country = {
                limit = { has_country_flag = wif_gp_tmp_aggpat }
                clr_country_flag = wif_gp_tmp_aggpat
            }
        }
    }
}

# THIS (aggressor) opens a proxy war on var:wif_gp_ev_target.
wif_gp_start_proxy_war = {
    add_to_variable = { global.wif_gp_px_next = 1 }
    add_to_variable = { global.wif_gp_px_count = 1 }
    set_variable = { wif_gp_px_id = global.wif_gp_px_next }
    set_variable = { wif_gp_px_side = 1 }
    set_variable = { wif_gp_px_patron = wif_gp_patron }
    set_country_flag = wif_gp_px_main
    var:wif_gp_ev_target = {
        set_variable = { wif_gp_px_id = global.wif_gp_px_next }
        set_variable = { wif_gp_px_side = 2 }
        set_variable = { wif_gp_px_patron = wif_gp_patron }
        set_country_flag = wif_gp_px_main
        PREV = { declare_war_on = { target = PREV type = annex_everything } }
    }
    news_event = { id = wif_gp.51 days = 1 }
    # Each patron backs its client.
    set_variable = { wif_gp_cw_patron = wif_gp_px_patron }
    wif_gp_sponsor_side = yes
    var:wif_gp_ev_target = {
        set_variable = { wif_gp_cw_patron = wif_gp_px_patron }
        wif_gp_sponsor_side = yes
    }
    log = "WiF GP: proxy war [?global.wif_gp_px_next]: [This.GetName] against [?This.wif_gp_ev_target.GetName]"
}

# Ends proxy war global.wif_gp_cur_id: white peace between every pair, clear
# all proxy data. wif_gp_px_flip = 1 first hands occupied states over.
wif_gp_end_proxy_war = {
    if = {
        limit = { check_variable = { global.wif_gp_px_flip = 1 } }
        every_state = {
            limit = {
                owner = { check_variable = { wif_gp_px_id = global.wif_gp_cur_id } }
                controller = { check_variable = { wif_gp_px_id = global.wif_gp_cur_id } }
                OR = {
                    AND = {
                        owner = { check_variable = { wif_gp_px_side = 1 } }
                        controller = { check_variable = { wif_gp_px_side = 2 } }
                    }
                    AND = {
                        owner = { check_variable = { wif_gp_px_side = 2 } }
                        controller = { check_variable = { wif_gp_px_side = 1 } }
                    }
                }
            }
            transfer_state_to = CONTROLLER
        }
    }
    every_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            check_variable = { wif_gp_px_side = 1 }
        }
        every_country = {
            limit = {
                check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
                check_variable = { wif_gp_px_side = 2 }
                has_war_with = PREV
            }
            PREV = { white_peace = { tag = PREV } }
        }
    }
    # A halted civil war: both halves stay apart and join their patrons.
    every_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            has_country_flag = wif_gp_px_civil
            check_variable = { global.wif_gp_px_flip = 1 }
            has_variable = wif_gp_px_patron
            is_in_faction = no
        }
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ has_global_flag = wif_gp_slot_{s}_used check_variable = {{ wif_gp_px_patron = global.wif_gp_slot_{s} }} }}
            wif_gp_join_slot_{s} = yes
        }}
'''
    t += '''    }
    every_country = {
        limit = { check_variable = { wif_gp_px_id = global.wif_gp_cur_id } }
        set_variable = { wif_gp_px_id = 0 }
        set_variable = { wif_gp_px_side = 0 }
        clear_variable = wif_gp_px_patron
        clr_country_flag = wif_gp_px_main
        clr_country_flag = wif_gp_px_civil
        clr_country_flag = wif_gp_px_widened
        clr_country_flag = wif_gp_px_handled
    }
    subtract_from_variable = { global.wif_gp_px_count = 1 }
    clamp_variable = { var = global.wif_gp_px_count min = 0 max = 99 }
    set_variable = { global.wif_gp_px_flip = 0 }
}

# Border-first: flag up to global.wif_gp_bfs_n states of THIS that touch the
# winning side (global.wif_gp_cur_id / wif_gp_win_side) or an already flagged
# state.
wif_gp_mark_border_states = {
    set_variable = { wif_gp_bfs_c = 0 }
    while_loop_effect = {
        limit = {
            check_variable = { wif_gp_bfs_c < global.wif_gp_bfs_n }
            any_owned_state = { wif_gp_bfs_frontier = yes }
        }
        random_owned_state = {
            limit = { wif_gp_bfs_frontier = yes }
            set_state_flag = wif_gp_bfs
        }
        add_to_variable = { wif_gp_bfs_c = 1 }
    }
}

wif_gp_clear_border_marks = {
    every_state = {
        limit = { has_state_flag = wif_gp_bfs }
        clr_state_flag = wif_gp_bfs
    }
}

# Weekly: settle proxy wars a main side is losing (60% surrender), and offer
# the losing patron a way out when a widened ally breaks.
wif_gp_proxy_war_weekly = {
    # Proxy wars that ended on their own (capitulation, annexation).
    every_country = {
        limit = {
            has_country_flag = wif_gp_px_main
            check_variable = { wif_gp_px_side = 1 }
            NOT = {
                any_country = {
                    check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                    check_variable = { wif_gp_px_side = 2 }
                    has_war_with = PREV
                }
            }
        }
        set_variable = { global.wif_gp_cur_id = wif_gp_px_id }
        set_variable = { global.wif_gp_px_flip = 0 }
        wif_gp_end_proxy_war = yes
    }
    every_country = {
        limit = {
            has_country_flag = wif_gp_px_main
            NOT = { has_country_flag = wif_gp_px_civil }
            surrender_progress > 0.6
        }
        set_variable = { global.wif_gp_cur_id = wif_gp_px_id }
        set_variable = { global.wif_gp_win_side = 3 }
        subtract_from_variable = { global.wif_gp_win_side = wif_gp_px_side }
        random_country = {
            limit = {
                check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
                check_variable = { wif_gp_px_side = global.wif_gp_win_side }
                has_country_flag = wif_gp_px_main
            }
            set_country_flag = wif_gp_px_winner_tmp
        }
        # Up to 6 states, border-first; the whole country if it has 6 or fewer.
        if = {
            limit = { check_variable = { num_owned_states < 7 } }
            random_country = {
                limit = { has_country_flag = wif_gp_px_winner_tmp }
                annex_country = { target = PREV transfer_troops = no }
            }
        }
        else = {
            set_variable = { global.wif_gp_bfs_n = 6 }
            wif_gp_mark_border_states = yes
            every_owned_state = {
                limit = { has_state_flag = wif_gp_bfs }
                random_country = {
                    limit = { has_country_flag = wif_gp_px_winner_tmp }
                    PREV = { transfer_state_to = PREV }
                }
            }
            wif_gp_clear_border_marks = yes
        }
        random_country = {
            limit = { has_country_flag = wif_gp_px_winner_tmp }
            news_event = { id = wif_gp.57 days = 1 }
            if = {
                limit = { has_variable = wif_gp_px_patron }
                var:wif_gp_px_patron = { add_to_variable = { wif_gp_cred = 8 } clamp_variable = { var = wif_gp_cred min = 0 max = 100 } }
            }
            clr_country_flag = wif_gp_px_winner_tmp
        }
        if = {
            limit = { has_variable = wif_gp_px_patron }
            var:wif_gp_px_patron = { add_to_variable = { wif_gp_cred = -8 } clamp_variable = { var = wif_gp_cred min = 0 max = 100 } }
        }
        set_variable = { global.wif_gp_px_flip = 0 }
        wif_gp_end_proxy_war = yes
    }
    # A widened ally breaks: its patron chooses.
    every_country = {
        limit = {
            has_country_flag = wif_gp_px_widened
            NOT = { has_country_flag = wif_gp_px_handled }
            surrender_progress > 0.6
        }
        set_country_flag = wif_gp_px_handled
        if = {
            limit = { has_variable = wif_gp_px_patron }
            var:wif_gp_px_patron = {
                set_variable = { wif_gp_ev_target = PREV }
                set_variable = { wif_gp_ev_px = PREV.wif_gp_px_id }
                country_event = { id = wif_gp.56 }
            }
        }
    }
}

# Patron scope, wif_gp_ev_px = war id, wif_gp_ev_target = the broken ally.
# Option 1: cut losses - the ally changes government to the winner's patron
# ideology and joins its bloc; the winning main proxy takes 3 border states
# (not in a civil war).
wif_gp_px_cut_losses = {
    set_variable = { global.wif_gp_cur_id = wif_gp_ev_px }
    set_variable = { global.wif_gp_win_side = 3 }
    var:wif_gp_ev_target = { subtract_from_variable = { global.wif_gp_win_side = wif_gp_px_side } }
    set_country_flag = wif_gp_px_loser_pat_tmp
    random_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            check_variable = { wif_gp_px_side = global.wif_gp_win_side }
            has_country_flag = wif_gp_px_main
        }
        set_country_flag = wif_gp_px_winner_tmp
    }
    var:wif_gp_ev_target = {
        if = {
            limit = {
                NOT = { any_country = { has_country_flag = wif_gp_px_winner_tmp has_country_flag = wif_gp_px_civil } }
            }
            set_variable = { global.wif_gp_bfs_n = 3 }
            wif_gp_mark_border_states = yes
            every_owned_state = {
                limit = { has_state_flag = wif_gp_bfs }
                random_country = {
                    limit = { has_country_flag = wif_gp_px_winner_tmp }
                    PREV = { transfer_state_to = PREV }
                }
            }
            wif_gp_clear_border_marks = yes
        }
        if = { limit = { is_in_faction = yes } leave_faction = yes }
    }
    set_variable = { global.wif_gp_px_flip = 0 }
    wif_gp_end_proxy_war = yes
    var:wif_gp_ev_target = {
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{
                has_global_flag = wif_gp_slot_{s}_used
                any_country = {{ has_country_flag = wif_gp_px_winner_tmp check_variable = {{ wif_gp_patron = global.wif_gp_slot_{s} }} }}
            }}
            wif_gp_set_gov_slot_{s} = yes
            wif_gp_join_slot_{s} = yes
        }}
'''
    t += '''    }
    every_country = {
        limit = { OR = { has_country_flag = wif_gp_px_winner_tmp has_country_flag = wif_gp_px_loser_pat_tmp } }
        clr_country_flag = wif_gp_px_winner_tmp
        clr_country_flag = wif_gp_px_loser_pat_tmp
    }
    add_to_variable = { wif_gp_cred = -10 }
    clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
    news_event = { id = wif_gp.57 days = 1 }
}

# Option 2: reach out - the losing main proxy is split in two along the front:
# the half facing the winners rises as a client of the winning patron.
wif_gp_px_reach_out = {
    set_variable = { global.wif_gp_cur_id = wif_gp_ev_px }
    set_variable = { global.wif_gp_win_side = 3 }
    var:wif_gp_ev_target = { subtract_from_variable = { global.wif_gp_win_side = wif_gp_px_side } }
    random_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            check_variable = { wif_gp_px_side = global.wif_gp_win_side }
            has_country_flag = wif_gp_px_main
        }
        set_country_flag = wif_gp_px_winner_tmp
    }
    random_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            NOT = { check_variable = { wif_gp_px_side = global.wif_gp_win_side } }
            has_country_flag = wif_gp_px_main
        }
        set_country_flag = wif_gp_px_split_tmp
    }
    set_variable = { global.wif_gp_px_flip = 0 }
    wif_gp_end_proxy_war = yes
    random_country = {
        limit = { has_country_flag = wif_gp_px_split_tmp }
        set_variable = { global.wif_gp_bfs_n = num_owned_states }
        divide_variable = { global.wif_gp_bfs_n = 2 }
        round_variable = global.wif_gp_bfs_n
        if = {
            limit = { check_variable = { num_owned_states < 4 } }
'''
    # too small: whole country flips to the winner side
    for s in SLOTS:
        t += f'''            if = {{
                limit = {{
                    has_global_flag = wif_gp_slot_{s}_used
                    any_country = {{ has_country_flag = wif_gp_px_winner_tmp check_variable = {{ wif_gp_patron = global.wif_gp_slot_{s} }} }}
                }}
                if = {{ limit = {{ is_in_faction = yes }} leave_faction = yes }}
                wif_gp_set_gov_slot_{s} = yes
                wif_gp_join_slot_{s} = yes
            }}
'''
    t += '''        }
        else = {
            # The war is over, so mark the states that face the old enemy.
            every_country = {
                limit = { has_country_flag = wif_gp_px_winner_tmp }
                set_variable = { wif_gp_px_id = global.wif_gp_cur_id }
                set_variable = { wif_gp_px_side = global.wif_gp_win_side }
            }
            wif_gp_mark_border_states = yes
            every_country = {
                limit = { has_country_flag = wif_gp_px_winner_tmp }
                set_variable = { wif_gp_px_id = 0 }
                set_variable = { wif_gp_px_side = 0 }
            }
            set_country_flag = wif_gp_px_splitting
'''
    for s in SLOTS:
        t += f'''            if = {{
                limit = {{
                    has_global_flag = wif_gp_slot_{s}_used
                    any_country = {{ has_country_flag = wif_gp_px_winner_tmp check_variable = {{ wif_gp_patron = global.wif_gp_slot_{s} }} }}
                    wif_gp_same_gov_as_slot_{s} = no
                }}
                set_variable = {{ global.wif_gp_split_slot = {s} }}
'''
        t += indent(slot_ideology_branch(s, lambda i: f'start_civil_war = {{ ideology = {i} size = 0.5 states_filter = {{ has_state_flag = wif_gp_bfs }} }}'), 4) + '\n'
        t += '            }\n'
    t += '''            wif_gp_clear_border_marks = yes
            # The new half: at peace with the old, and in the winner's bloc.
            every_country = {
                limit = {
                    civilwar_target = PREV
                    has_war_with = PREV
                }
                PREV = { white_peace = { tag = PREV } }
'''
    for s in SLOTS:
        t += f'''                if = {{
                    limit = {{ check_variable = {{ global.wif_gp_split_slot = {s} }} }}
                    wif_gp_join_slot_{s} = yes
                }}
'''
    t += '''            }
            clr_country_flag = wif_gp_px_splitting
            set_variable = { global.wif_gp_split_slot = 0 }
        }
        clr_country_flag = wif_gp_px_split_tmp
    }
    every_country = {
        limit = { has_country_flag = wif_gp_px_winner_tmp }
        clr_country_flag = wif_gp_px_winner_tmp
    }
    add_to_variable = { wif_gp_cred = -5 }
    clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
    news_event = { id = wif_gp.57 days = 1 }
}

# Option 3 / decision: escalate. The proxy war becomes an ordinary war, the
# patron and its whole faction join, and the other bloc is forced in.
wif_gp_px_escalate = {
    set_variable = { global.wif_gp_cur_id = wif_gp_ev_px }
    set_country_flag = wif_gp_px_esc_pat
    random_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            has_country_flag = wif_gp_px_main
            var:wif_gp_px_patron = { has_country_flag = wif_gp_px_esc_pat }
        }
        set_country_flag = wif_gp_px_own_main_tmp
    }
    clr_country_flag = wif_gp_px_esc_pat
    random_country = {
        limit = {
            check_variable = { wif_gp_px_id = global.wif_gp_cur_id }
            has_country_flag = wif_gp_px_main
            NOT = { has_country_flag = wif_gp_px_own_main_tmp }
        }
        set_country_flag = wif_gp_px_enemy_main_tmp
        if = { limit = { has_variable = wif_gp_px_patron } var:wif_gp_px_patron = { set_country_flag = wif_gp_px_enemy_pat_tmp } }
    }
    # No longer a proxy war: lift the join block before anyone declares.
    every_country = {
        limit = { check_variable = { wif_gp_px_id = global.wif_gp_cur_id } }
        set_variable = { wif_gp_px_id = 0 }
        set_variable = { wif_gp_px_side = 0 }
        clear_variable = wif_gp_px_patron
        clr_country_flag = wif_gp_px_main
        clr_country_flag = wif_gp_px_civil
        clr_country_flag = wif_gp_px_widened
        clr_country_flag = wif_gp_px_handled
    }
    subtract_from_variable = { global.wif_gp_px_count = 1 }
    clamp_variable = { var = global.wif_gp_px_count min = 0 max = 99 }
    # Our bloc in.
    every_country = {
        limit = {
            OR = {
                tag = PREV
                AND = { is_in_faction = yes is_in_faction_with = PREV }
            }
            NOT = { has_country_flag = wif_gp_px_own_main_tmp }
        }
        random_country = {
            limit = { has_country_flag = wif_gp_px_enemy_main_tmp }
            PREV = {
                if = {
                    limit = { NOT = { has_war_with = PREV } }
                    declare_war_on = { target = PREV type = annex_everything }
                }
            }
        }
    }
    # Their bloc in.
    every_country = {
        limit = {
            OR = {
                has_country_flag = wif_gp_px_enemy_pat_tmp
                any_country = { has_country_flag = wif_gp_px_enemy_pat_tmp is_in_faction_with = PREV }
            }
            NOT = { has_country_flag = wif_gp_px_enemy_main_tmp }
        }
        random_country = {
            limit = { has_country_flag = wif_gp_px_own_main_tmp }
            PREV = {
                if = {
                    limit = { NOT = { has_war_with = PREV } }
                    declare_war_on = { target = PREV type = annex_everything }
                }
            }
        }
    }
    every_country = {
        limit = {
            OR = {
                has_country_flag = wif_gp_px_own_main_tmp
                has_country_flag = wif_gp_px_enemy_main_tmp
                has_country_flag = wif_gp_px_enemy_pat_tmp
            }
        }
        clr_country_flag = wif_gp_px_own_main_tmp
        clr_country_flag = wif_gp_px_enemy_main_tmp
        clr_country_flag = wif_gp_px_enemy_pat_tmp
    }
    news_event = { id = wif_gp.58 days = 1 }
    log = "WiF GP: [This.GetName] escalated a proxy war into a bloc war"
}

'''

    # ------------------------------------------------------------- nuclear
    t += '''# ===========================================================================
# NUCLEAR DOCTRINE - AI launches (weekly, country scope = ROOT from on_weekly)
#   1 Last Resort    - 70% surrender, or an ally (faction/puppet) was nuked
#   2 Threat Launch  - 20% surrender, or 4+ allies/puppets capitulated
#   3 First Strike   - vs a nuclear enemy: at once, silos and air bases first
#   4 Purifying Flame - at war: everything
# ===========================================================================
wif_gp_nuclear_ai_weekly = {
    if = { limit = { NOT = { check_variable = { wif_gp_doctrine > 0 } } } set_variable = { wif_gp_doctrine = 1 } }
    if = {
        limit = { has_war = no }
        set_variable = { wif_gp_fallen_allies = 0 }
        set_variable = { wif_gp_strikes = 0 }
        clr_country_flag = wif_gp_mad
    }
    if = {
        limit = {
            is_ai = yes
            has_war = yes
            num_of_nukes > 0
            wif_gp_can_deliver = yes
        }
        set_temp_variable = { shots = 0 }
        clr_country_flag = wif_gp_first_strike_mode
        set_temp_variable = { mad_shot = 0 }
        if = {
            limit = {
                has_country_flag = wif_gp_mad
                has_variable = wif_gp_mad_target
                var:wif_gp_mad_target = { has_war_with = ROOT }
            }
            set_temp_variable = { mad_shot = 1 }
        }
        if = {
            limit = { check_variable = { wif_gp_doctrine = 4 } }
            set_temp_variable = { shots = 3 }
        }
        else_if = {
            limit = {
                check_variable = { wif_gp_doctrine = 3 }
                any_country = { has_war_with = ROOT wif_gp_nuclear_power = yes }
            }
            set_temp_variable = { shots = 2 }
            set_country_flag = wif_gp_first_strike_mode
        }
        else_if = {
            limit = {
                OR = {
                    surrender_progress > 0.7
                    check_temp_variable = { mad_shot = 1 }
                    AND = {
                        check_variable = { wif_gp_doctrine > 1 }
                        OR = {
                            surrender_progress > 0.2
                            check_variable = { wif_gp_fallen_allies > 3 }
                        }
                    }
                }
            }
            set_temp_variable = { shots = 1 }
            if = { limit = { surrender_progress > 0.7 } set_temp_variable = { shots = 2 } }
        }
        while_loop_effect = {
            limit = {
                check_temp_variable = { shots > 0 }
                num_of_nukes > 0
            }
            subtract_from_temp_variable = { shots = 1 }
            wif_gp_pick_nuke_target = yes
            if = {
                limit = { has_country_flag = wif_gp_nt_found }
                clr_country_flag = wif_gp_nt_found
                launch_nuke = { state = var:wif_gp_nt use_nuke = yes }
                add_to_variable = { wif_gp_strikes = 1 }
                log = "WiF GP: [This.GetName] (doctrine [?This.wif_gp_doctrine]) launched a nuke at [?This.wif_gp_nt.GetName]"
            }
        }
    }
}

wif_gp_pick_nuke_target = {
    clr_country_flag = wif_gp_nt_found
    # Retaliation goes to whoever struck us.
    if = {
        limit = { has_country_flag = wif_gp_mad has_variable = wif_gp_mad_target }
        var:wif_gp_mad_target = { set_country_flag = wif_gp_mad_target_tmp }
    }
    if = {
        limit = { any_state = { wif_gp_nt_mad = yes } }
        if = {
            limit = { any_state = { wif_gp_nt_mad = yes wif_gp_nt_industry = yes } }
            random_state = { limit = { wif_gp_nt_mad = yes wif_gp_nt_industry = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
        }
        else = {
            random_state = { limit = { wif_gp_nt_mad = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
        }
        set_country_flag = wif_gp_nt_found
    }
    every_country = {
        limit = { has_country_flag = wif_gp_mad_target_tmp }
        clr_country_flag = wif_gp_mad_target_tmp
    }
    if = {
        limit = { NOT = { has_country_flag = wif_gp_nt_found } }
        if = {
            limit = { check_variable = { wif_gp_doctrine = 4 } }
            if = {
                limit = { any_state = { wif_gp_nt_city = yes } }
                random_state = { limit = { wif_gp_nt_city = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
            else_if = {
                limit = { any_state = { wif_gp_nt_anything = yes } }
                random_state = { limit = { wif_gp_nt_anything = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
        }
        else = {
            if = {
                limit = { has_country_flag = wif_gp_first_strike_mode any_state = { wif_gp_nt_silo = yes } }
                random_state = { limit = { wif_gp_nt_silo = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
            else_if = {
                limit = { has_country_flag = wif_gp_first_strike_mode any_state = { wif_gp_nt_airbase = yes } }
                random_state = { limit = { wif_gp_nt_airbase = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
            else_if = {
                limit = { check_variable = { wif_gp_strikes < 4 } any_state = { wif_gp_nt_industry = yes } }
                random_state = { limit = { wif_gp_nt_industry = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
            else_if = {
                limit = { any_state = { wif_gp_nt_city = yes } }
                random_state = { limit = { wif_gp_nt_city = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
            else_if = {
                limit = { any_state = { wif_gp_nt_industry = yes } }
                random_state = { limit = { wif_gp_nt_industry = yes } set_variable = { ROOT.wif_gp_nt = THIS } }
                set_country_flag = wif_gp_nt_found
            }
        }
    }
}

# on_nuke_drop: ROOT = nuker, FROM = the state.
wif_gp_on_nuke = {
    FROM = {
        set_temp_variable = { p = state_population_k }
        multiply_temp_variable = { p = -80 }
        add_manpower = var:p
        set_state_flag = { flag = wif_gp_fallout value = 1 days = ''' + str(FALLOUT_DAYS) + ''' }
        if = {
            limit = { rocket_site > 0 }
            remove_building = { type = rocket_site level = 1 }
        }
        if = {
            limit = { air_base > 0 }
            damage_building = { type = air_base damage = 20 repair_speed_modifier = -0.9 }
        }
        # Mutually assured destruction: the owner, its faction and its
        # overlord/puppets may now strike back at the nuker.
        if = {
            limit = { OWNER = { has_war_with = ROOT } }
            OWNER = {
                every_country = {
                    limit = {
                        OR = {
                            tag = PREV
                            is_in_faction_with = PREV
                            is_subject_of = PREV
                            has_subject = PREV
                        }
                        has_war_with = ROOT
                    }
                    set_country_flag = { flag = wif_gp_mad value = 1 days = 365 }
                    set_variable = { wif_gp_mad_target = ROOT }
                }
            }
        }
    }
}

# Weekly: keep irradiated air bases grounded.
wif_gp_fallout_weekly = {
    every_state = {
        limit = {
            has_state_flag = wif_gp_fallout
            air_base > 0
        }
        damage_building = { type = air_base damage = 20 repair_speed_modifier = -0.9 }
    }
}

'''

    # ------------------------------------------------------------- NAM
    t += '''# ===========================================================================
# NON-ALIGNED MOVEMENT
# ===========================================================================
wif_gp_nam_upkeep = {
    if = {
        limit = { has_global_flag = wif_gp_nam_exists }
        set_variable = { global.wif_gp_nam_count = 0 }
        every_country = {
            limit = { wif_gp_nam_member = yes }
            if = {
                limit = {
                    OR = {
                        is_in_faction = yes
                        is_subject = yes
                        check_variable = { wif_gp_tier > 2 }
                    }
                }
                remove_ideas = wif_gp_nam_member_idea
            }
            else = { add_to_variable = { global.wif_gp_nam_count = 1 } }
        }
        if = {
            limit = {
                NOT = { has_global_flag = wif_gp_nam_grace }
                check_variable = { global.wif_gp_nam_count < 3 }
            }
            clr_global_flag = wif_gp_nam_exists
            every_country = {
                limit = { wif_gp_nam_member = yes }
                remove_ideas = wif_gp_nam_member_idea
            }
            news_event = { id = wif_gp.83 days = 1 }
        }
        else = {
            # The leader left: the strongest member takes over.
            if = {
                limit = { var:global.wif_gp_nam_leader = { wif_gp_nam_member = no } }
                set_variable = { global.wif_gp_best_score = 0 }
                every_country = {
                    limit = { wif_gp_nam_member = yes }
                    if = {
                        limit = { check_variable = { wif_gp_score > global.wif_gp_best_score } }
                        set_variable = { global.wif_gp_best_score = wif_gp_score }
                        set_variable = { global.wif_gp_nam_leader = THIS }
                    }
                }
            }
            if = {
                limit = { NOT = { has_global_flag = wif_gp_nam_summit_cd } }
                set_global_flag = { flag = wif_gp_nam_summit_cd value = 1 days = 1200 }
                every_country = {
                    limit = { wif_gp_nam_member = yes }
                    add_timed_idea = { idea = wif_gp_nam_summit_idea days = 365 }
                }
                var:global.wif_gp_nam_leader = {
                    add_political_power = 50
                    news_event = { id = wif_gp.82 days = 1 }
                }
            }
        }
    }
}

'''

    # ------------------------------------------------------------- races
    t += '''# ===========================================================================
# PRESTIGE RACES & PROLIFERATION
# ===========================================================================
wif_gp_prestige_races = {
'''
    for n, (k, _d, trig) in enumerate(RACES):
        t += f'''    if = {{
        limit = {{
            NOT = {{ has_global_flag = wif_gp_race_{k} }}
            any_country = {{ {trig} }}
        }}
        set_global_flag = wif_gp_race_{k}
        random_country = {{
            limit = {{ {trig} }}
            set_variable = {{ global.wif_gp_race_{k}_winner = THIS }}
            set_country_flag = wif_gp_race_won_{k}
            news_event = {{ id = wif_gp.{70 + n} days = 1 }}
            if = {{
                limit = {{ wif_gp_is_global = yes }}
                add_to_variable = {{ wif_gp_cred = 10 }}
                clamp_variable = {{ var = wif_gp_cred min = 0 max = 100 }}
            }}
            set_country_flag = wif_gp_race_winner_tmp
        }}
        every_country = {{
            limit = {{
                check_variable = {{ wif_gp_tier > 1 }}
                NOT = {{ has_country_flag = wif_gp_race_winner_tmp }}
                NOT = {{ has_idea = wif_gp_cannot_fall_behind_idea }}
            }}
            add_timed_idea = {{ idea = wif_gp_cannot_fall_behind_idea days = 365 }}
        }}
        every_country = {{
            limit = {{ has_country_flag = wif_gp_race_winner_tmp }}
            clr_country_flag = wif_gp_race_winner_tmp
        }}
    }}
'''
    t += '''}

# A country below Growing Superpower builds the bomb after someone else did.
wif_gp_proliferation = {
    if = {
        limit = { has_global_flag = wif_gp_race_atomic }
        every_country = {
            limit = {
                has_tech = nukes
                NOT = { has_country_flag = wif_gp_nuclear_known }
                NOT = { check_variable = { wif_gp_tier > 2 } }
            }
            set_country_flag = wif_gp_nuclear_known
            if = {
                limit = { NOT = { has_country_flag = wif_gp_race_won_atomic } }
                news_event = { id = wif_gp.85 days = 1 }
            }
        }
    }
}
'''
    return t


# ---------------------------------------------------------------------------
# On actions
# ---------------------------------------------------------------------------
def gen_on_actions():
    t = HEADER + '''on_actions = {
    on_startup = {
        effect = {
            if = {
                limit = { NOT = { has_global_flag = wif_gp_started } }
                set_global_flag = wif_gp_started
                set_variable = { global.wif_gp_global_count = 0 }
                set_variable = { global.wif_gp_growing_count = 0 }
                set_variable = { global.wif_gp_px_count = 0 }
                set_variable = { global.wif_gp_px_next = 0 }
                set_variable = { global.wif_gp_top = 1 }
                wif_gp_init_regions = yes
                # Nuclear doctrines that do not start on Last Resort.
                every_country = {
                    limit = { OR = { original_tag = GER original_tag = JAP original_tag = SOV } }
                    set_variable = { wif_gp_doctrine = 2 }
                }
            }
        }
    }

    on_monthly = {
        effect = {
            if = {
                limit = { NOT = { has_global_flag = wif_gp_month_lock } }
                set_global_flag = { flag = wif_gp_month_lock value = 1 days = 25 }
                wif_gp_monthly = yes
            }
            # The Ordensstaat always burns.
            if = {
                limit = {
                    original_tag = OSB
                    NOT = { check_variable = { wif_gp_doctrine = 4 } }
                    NOT = { has_country_flag = wif_gp_doctrine_scripted }
                }
                set_variable = { wif_gp_doctrine = 4 }
            }
        }
    }

    on_weekly = {
        effect = {
            if = {
                limit = { NOT = { has_global_flag = wif_gp_week_lock } }
                set_global_flag = { flag = wif_gp_week_lock value = 1 days = 6 }
                wif_gp_fallout_weekly = yes
                wif_gp_proxy_war_weekly = yes
            }
            if = {
                limit = { wif_gp_nuclear_power = yes }
                wif_gp_nuclear_ai_weekly = yes
            }
        }
    }

    on_nuke_drop = {
        effect = { wif_gp_on_nuke = yes }
    }

    # ROOT = capitulated, FROM = winner.
    on_capitulation = {
        effect = {
            every_country = {
                limit = {
                    OR = {
                        AND = { is_in_faction = yes is_in_faction_with = ROOT }
                        has_subject = ROOT
                    }
                    NOT = { tag = ROOT }
                }
                add_to_variable = { wif_gp_fallen_allies = 1 }
            }
            if = {
                limit = { wif_gp_is_global = yes }
                add_to_variable = { wif_gp_cred = -15 }
                clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
            }
            every_country = {
                limit = { wif_gp_is_global = yes has_war_with = ROOT }
                add_to_variable = { wif_gp_cred = 5 }
                clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
            }
            if = {
                limit = { has_country_flag = wif_gp_has_patron }
                var:wif_gp_patron = {
                    if = {
                        limit = { has_war_with = FROM }
                        add_to_variable = { wif_gp_cred = -5 }
                        clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
                    }
                }
            }
        }
    }

    # ROOT declares war on FROM.
    on_declare_war = {
        effect = {
            # A sphere member attacked: its patron has 60 days to respond.
            if = {
                limit = {
                    NOT = { wif_gp_in_proxy = yes }
                    FROM = {
                        has_country_flag = wif_gp_has_patron
                        var:wif_gp_patron = {
                            NOT = { tag = ROOT }
                            NOT = { is_in_faction_with = ROOT }
                        }
                    }
                }
                FROM = {
                    set_variable = { wif_gp_attacker = ROOT }
                    set_country_flag = { flag = wif_gp_defend_window value = 1 days = 60 }
                    set_country_flag = wif_gp_defend_pending
                    var:wif_gp_patron = {
                        if = {
                            limit = { is_ai = no }
                            set_variable = { wif_gp_ev_target = PREV }
                            country_event = { id = wif_gp.30 }
                        }
                    }
                }
            }
            # A Global Power attacking a non-aligned country: the movement protests.
            if = {
                limit = {
                    wif_gp_is_global = yes
                    FROM = { wif_gp_nam_member = yes }
                }
                add_to_variable = { wif_gp_cred = -15 }
                clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
                every_country = {
                    limit = { wif_gp_nam_member = yes }
                    add_opinion_modifier = { target = ROOT modifier = wif_gp_nam_aggression }
                }
            }
        }
    }

    # Nobody joins a proxy war. ROOT = attacking side, FROM = defending side.
    on_war_relation_added = {
        effect = {
            if = {
                limit = {
                    OR = {
                        ROOT = { wif_gp_in_proxy = yes }
                        FROM = { wif_gp_in_proxy = yes }
                    }
                    NOT = {
                        AND = {
                            ROOT = { wif_gp_in_proxy = yes }
                            FROM = { wif_gp_in_proxy = yes }
                            ROOT = { check_variable = { wif_gp_px_id = FROM.wif_gp_px_id } }
                            NOT = { ROOT = { check_variable = { wif_gp_px_side = FROM.wif_gp_px_side } } }
                        }
                    }
                }
                log = "WiF GP: [Root.GetName] and [From.GetName] kept out of a proxy war"
                ROOT = { white_peace = { tag = FROM } }
            }
        }
    }
}
'''
    return t


# ---------------------------------------------------------------------------
# Ideas, dynamic modifiers, opinion modifiers
# ---------------------------------------------------------------------------
def gen_ideas():
    return HEADER + '''ideas = {
    country = {
        wif_gp_tier_global = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_central_management
            modifier = {
                political_power_gain = 0.25
                research_speed_factor = 0.03
                justify_war_goal_time = -0.1
            }
        }
        wif_gp_tier_growing = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_improved_industries
            modifier = {
                research_speed_factor = 0.05
                industrial_capacity_factory = 0.05
            }
        }
        wif_gp_tier_great = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_flexible_foreign_policy
            modifier = {
                political_power_gain = 0.1
            }
        }
        wif_gp_tier_regional = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_local_self_management
            modifier = {
                political_power_gain = 0.05
            }
        }
        wif_gp_overshadowed_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_disjointed_gov
            modifier = {
                stability_factor = -0.05
                political_power_gain = -0.1
            }
        }
        wif_gp_lost_greatness_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = yes }
            removal_cost = -1
            picture = generic_fortify_the_borders
            modifier = {
                war_support_factor = 0.1
                justify_war_goal_time = -0.25
            }
        }
        wif_gp_new_role_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = yes }
            removal_cost = -1
            picture = generic_economic_recovery
            modifier = {
                stability_factor = 0.1
            }
        }
        wif_gp_sphere_holds_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_economic_recovery
            modifier = {
                stability_factor = 0.05
                war_support_factor = 0.05
            }
        }
        wif_gp_overstretched_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_economic_crisis
            modifier = {
                stability_factor = -0.1
                consumer_goods_factor = 0.05
            }
        }
        wif_gp_cannot_fall_behind_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_intel_bonus
            modifier = {
                research_speed_factor = 0.05
            }
        }
        wif_gp_nam_member_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_conference
            modifier = {
                stability_factor = 0.03
                political_power_gain = 0.05
            }
        }
        wif_gp_nam_summit_idea = {
            allowed = { always = no }
            allowed_civil_war = { always = no }
            removal_cost = -1
            picture = generic_conference
            modifier = {
                stability_factor = 0.05
                political_power_gain = 0.1
            }
        }
    }
}
'''


def gen_dynamic_modifiers():
    return HEADER + '''# Global Commitments: 2% consumer goods per claimed region (wif_gp_cg).
wif_gp_commitments = {
    icon = GFX_idea_generic_central_management
    consumer_goods_factor = wif_gp_cg
}
'''


def gen_opinion_modifiers():
    return HEADER + '''opinion_modifiers = {
    wif_gp_nam_aggression = {
        value = -50
        decay = 1
    }
}
'''


# ---------------------------------------------------------------------------
# AI strategy
# ---------------------------------------------------------------------------
def gen_ai():
    t = HEADER
    t += '''# Nuclear Ambition: Great Powers and up race for the Global Power requirements
# once the Atomic Age has begun. Special projects get their push from the
# patched copies in common/special_projects/projects.
wif_gp_nuclear_ambition_research = {
    allowed = { always = yes }
    enable = { has_country_flag = wif_gp_nuclear_ambition }
    abort_when_not_enabled = yes
'''
    for tech, v in [('atomic_research', 300), ('basic_large_airframe', 150), ('improved_large_airframe', 200),
                    ('advanced_large_airframe', 300), ('rocket_engines', 150), ('strategic_bomber2', 100),
                    ('strategic_bomber3', 100)]:
        t += f'    ai_strategy = {{ type = research_weight_factor id = {tech} value = {v} }}\n'
    t += '''}

wif_gp_nuclear_ambition_facility = {
    allowed = { always = yes }
    enable = {
        has_country_flag = wif_gp_nuclear_ambition
        nuclear_facility < 1
    }
    abort_when_not_enabled = yes
    ai_strategy = { type = build_building id = nuclear_facility value = 150 }
}

wif_gp_nuclear_ambition_air_facility = {
    allowed = { always = yes }
    enable = {
        has_country_flag = wif_gp_nuclear_ambition
        has_tech = nukes
        air_facility < 1
    }
    abort_when_not_enabled = yes
    ai_strategy = { type = build_building id = air_facility value = 120 }
}

wif_gp_rocket_sites = {
    allowed = { always = yes }
    enable = {
        has_country_flag = wif_gp_nuclear_ambition
        OR = {
            is_special_project_completed = sp:sp_rockets_medium_range_ballistic_missile
            is_special_project_completed = sp:sp_rockets_long_range_ballistic_missile
        }
    }
    abort_when_not_enabled = yes
    ai_strategy = { type = build_building id = rocket_site value = 40 }
}

# Arms race: the rival has more military factories.
wif_gp_arms_race = {
    allowed = { always = yes }
    enable = { has_country_flag = wif_gp_arms_race }
    abort_when_not_enabled = yes
    ai_strategy = { type = build_building id = arms_factory value = 50 }
}

'''
    return t


# ---------------------------------------------------------------------------
# Decisions
# ---------------------------------------------------------------------------
def gen_categories():
    return HEADER + '''wif_gp_weltpolitik_category = {
    icon = GFX_decision_category_generic_foreign_policy
    priority = 150
    visible_when_empty = yes
    visible = { wif_gp_is_global = yes }
}

wif_gp_nuclear_category = {
    icon = GFX_decision_category_generic_crisis
    priority = 140
    visible_when_empty = yes
    visible = { wif_gp_nuclear_power = yes }
}

wif_gp_nam_category = {
    icon = GFX_decision_category_generic_independence
    priority = 130
    visible_when_empty = yes
    visible = {
        OR = {
            wif_gp_nam_member = yes
            AND = {
                wif_gp_nam_eligible = yes
                check_variable = { global.wif_gp_global_count > 1 }
            }
        }
    }
}
'''


def gen_decisions():
    t = HEADER + 'wif_gp_weltpolitik_category = {\n'

    # Claims
    for k, _n, _s in REGIONS:
        t += sub('''
    wif_gp_claim_@K@ = {
        icon = generic_form_nation
        cost = @PP@
        visible = {
            wif_gp_is_global = yes
            NOT = { has_country_flag = wif_gp_claim_@K@ }
        }
        available = {
            check_variable = { wif_gp_cred > @CRED1@ }
            check_variable = { wif_gp_claims < @MAX@ }
        }
        complete_effect = {
            set_country_flag = wif_gp_claim_@K@
            add_to_variable = { wif_gp_claims = 1 }
            add_to_variable = { wif_gp_cred = -@CRED@ }
            custom_effect_tooltip = wif_gp_claim_tt
        }
        ai_will_do = {
            base = 0
            # Within what we can carry: our home region first, then contested ones.
            modifier = {
                add = 10
                check_variable = { wif_gp_claims < wif_gp_claim_cap }
                has_political_power > @PP2@
            }
            modifier = { factor = 10 wif_gp_capital_in_@K@ = yes }
            modifier = {
                factor = 2
                any_country = { wif_gp_capital_in_@K@ = yes has_country_flag = wif_gp_has_patron var:wif_gp_patron = { tag = ROOT } }
            }
            modifier = {
                factor = 1.5
                any_country = { wif_gp_is_global = yes NOT = { tag = ROOT } has_country_flag = wif_gp_claim_@K@ }
            }
            # The gamble: one region past capacity, only while the rival is in trouble.
            modifier = {
                add = 4
                NOT = { check_variable = { wif_gp_claims < wif_gp_claim_cap } }
                check_variable = { wif_gp_claims < wif_gp_claim_cap_gamble }
                has_variable = wif_gp_rival
                var:wif_gp_rival = { has_country_flag = wif_gp_strain }
                check_variable = { wif_gp_cred > 59 }
                has_political_power > @PP2@
            }
        }
    }

    wif_gp_abandon_@K@ = {
        icon = generic_break_treaty
        cost = 0
        visible = {
            wif_gp_is_global = yes
            has_country_flag = wif_gp_claim_@K@
        }
        complete_effect = {
            clr_country_flag = wif_gp_claim_@K@
            add_to_variable = { wif_gp_claims = -1 }
            add_to_variable = { wif_gp_cred = 5 }
            clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
        }
        ai_will_do = {
            base = 0
            modifier = {
                add = 5
                check_variable = { wif_gp_claims > wif_gp_claim_cap }
                wif_gp_capital_in_@K@ = no
                NOT = { any_country = { wif_gp_capital_in_@K@ = yes has_country_flag = wif_gp_has_patron var:wif_gp_patron = { tag = ROOT } } }
            }
        }
    }
''', K=k, PP=CLAIM_PP, PP2=CLAIM_PP + 50, CRED=CLAIM_CRED, CRED1=CLAIM_CRED - 1, MAX=MAX_CLAIMS)

    # Influence campaign - one decision per slot so the effect knows the slot
    for s in SLOTS:
        t += sub('''
    wif_gp_influence_@S@ = {
        icon = generic_political_discourse
        cost = 50
        target_trigger = {
            wif_gp_valid_influence_target = yes
            FROM = { NOT = { has_country_flag = wif_gp_camp_@S@ } }
        }
        visible = { wif_gp_is_global = yes check_variable = { wif_gp_slot = @S@ } }
        days_re_enable = 30
        complete_effect = {
            FROM = {
                set_country_flag = { flag = wif_gp_camp_@S@ value = 1 days = 180 }
                add_to_variable = { wif_gp_inf_@S@ = 5 }
                add_to_variable = { wif_gp_fav_@S@ = 5 }
                clamp_variable = { var = wif_gp_inf_@S@ min = 0 max = 100 }
            }
            custom_effect_tooltip = wif_gp_influence_tt
        }
        ai_will_do = {
            base = 0
            modifier = { add = 5 has_political_power > 80 }
            modifier = { factor = 2 FROM = { wif_gp_same_gov_as_slot_@S@ = yes } }
            modifier = { factor = 2 FROM = { check_variable = { wif_gp_inf_@S@ > 39 } } }
            modifier = { factor = 1.5 FROM = { check_variable = { wif_gp_tier = 1 } } }
            modifier = { factor = 0.5 FROM = { check_variable = { wif_gp_tier = 2 } } }
            modifier = { factor = 0.5 FROM = { wif_gp_nam_member = yes } }
            modifier = { factor = 0 has_country_flag = wif_gp_crisis }
        }
    }
''', S=s)

    # Rival tools and defences (targeted)
    for s in SLOTS:
        t += sub('''
    wif_gp_fund_dissidents_@S@ = {
        icon = generic_ignite_civil_war
        cost = 75
        target_trigger = {
            wif_gp_from_in_rival_sphere_@S@ = yes
            FROM = { NOT = { has_country_flag = wif_gp_destabilised } }
        }
        visible = { wif_gp_is_global = yes check_variable = { wif_gp_slot = @S@ } }
        complete_effect = {
            FROM = {
                set_country_flag = { flag = wif_gp_destabilised value = 1 days = 180 }
                add_to_variable = { wif_gp_inf_@S@ = 8 }
                clamp_variable = { var = wif_gp_inf_@S@ min = 0 max = 100 }
''', S=s)
        t += indent(slot_ideology_branch(s, lambda i: f'add_popularity = {{ ideology = {i} popularity = 0.04 }}'), 4) + '\n'
        t += sub('''            }
            custom_effect_tooltip = wif_gp_fund_dissidents_tt
        }
        ai_will_do = {
            base = 0
            modifier = { add = 3 has_political_power > 120 }
            modifier = { factor = 3 var:wif_gp_rival = { has_country_flag = wif_gp_strain } }
            modifier = { factor = 0 has_country_flag = wif_gp_strain }
        }
    }

    wif_gp_back_secessionists_@S@ = {
        icon = generic_independence
        cost = 100
        target_trigger = {
            wif_gp_from_in_rival_sphere_@S@ = yes
            FROM = {
                is_subject = yes
                NOT = { has_country_flag = wif_gp_secession }
            }
        }
        visible = { wif_gp_is_global = yes check_variable = { wif_gp_slot = @S@ } }
        complete_effect = {
            FROM = {
                set_country_flag = { flag = wif_gp_secession value = 1 days = 365 }
                add_autonomy_ratio = { value = 0.15 localization = wif_gp_secession_autonomy }
            }
        }
        ai_will_do = {
            base = 0
            modifier = { add = 3 has_political_power > 150 var:wif_gp_rival = { has_country_flag = wif_gp_strain } }
        }
    }

    wif_gp_stoke_tensions_@S@ = {
        icon = generic_police_action
        cost = 50
        target_trigger = {
            wif_gp_from_in_rival_sphere_@S@ = yes
            FROM = {
                wif_gp_is_proxy_size = yes
                NOT = { has_country_flag = wif_gp_border_tension }
                any_neighbor_country = {
                    wif_gp_is_proxy_size = yes
                    has_country_flag = wif_gp_has_patron
                    var:wif_gp_patron = { tag = ROOT }
                }
            }
        }
        visible = { wif_gp_is_global = yes check_variable = { wif_gp_slot = @S@ } }
        complete_effect = {
            FROM = { set_country_flag = { flag = wif_gp_border_tension value = 1 days = 365 } }
            custom_effect_tooltip = wif_gp_stoke_tensions_tt
        }
        ai_will_do = {
            base = 0
            modifier = { add = 1 has_political_power > 150 check_variable = { wif_gp_cred > 50 } }
        }
    }

    wif_gp_probe_@S@ = {
        icon = generic_military
        cost = 50
        days_re_enable = 365
        target_trigger = {
            wif_gp_from_in_rival_sphere_@S@ = yes
            FROM = { wif_gp_is_proxy_size = yes }
        }
        visible = {
            wif_gp_is_global = yes
            check_variable = { wif_gp_slot = @S@ }
            is_ai = no
        }
        complete_effect = {
            var:wif_gp_rival = {
                set_variable = { wif_gp_ev_power = PREV }
                set_variable = { wif_gp_ev_target = FROM }
                country_event = { id = wif_gp.31 }
            }
            custom_effect_tooltip = wif_gp_probe_tt
        }
        ai_will_do = { base = 0 }
    }

    wif_gp_subsidies_@S@ = {
        icon = generic_fundraising
        cost = 75
        days_re_enable = 90
        target_trigger = {
            wif_gp_root_is_from_patron = yes
            FROM = { NOT = { has_country_flag = wif_gp_subsidised } }
        }
        visible = { wif_gp_is_global = yes check_variable = { wif_gp_slot = @S@ } }
        complete_effect = {
            FROM = {
                set_country_flag = { flag = wif_gp_subsidised value = 1 days = 180 }
                add_to_variable = { wif_gp_inf_@S@ = 20 }
                add_to_variable = { wif_gp_fav_@S@ = 10 }
                clamp_variable = { var = wif_gp_inf_@S@ min = 0 max = 100 }
                clamp_variable = { var = wif_gp_fav_@S@ min = 0 max = 100 }
            }
        }
        ai_will_do = {
            base = 0
            modifier = { add = 8 has_country_flag = wif_gp_strain FROM = { check_variable = { wif_gp_loyalty < 40 } } }
        }
    }

    wif_gp_crackdown_@S@ = {
        icon = generic_arrest
        cost = 40
        target_trigger = {
            wif_gp_root_is_from_patron = yes
            FROM = { NOT = { has_country_flag = wif_gp_resentment } }
        }
        visible = {
            wif_gp_is_global = yes
            check_variable = { wif_gp_slot = @S@ }
            has_country_flag = wif_gp_strain
        }
        complete_effect = {
            FROM = {
                set_country_flag = { flag = wif_gp_resentment value = 1 days = 365 }
                add_to_variable = { wif_gp_inf_@S@ = 15 }
                add_to_variable = { wif_gp_fav_@S@ = -20 }
                clamp_variable = { var = wif_gp_inf_@S@ min = 0 max = 100 }
                clamp_variable = { var = wif_gp_fav_@S@ min = 0 max = 100 }
            }
            custom_effect_tooltip = wif_gp_crackdown_tt
        }
        ai_will_do = {
            base = 0
            modifier = { add = 4 has_country_flag = wif_gp_crisis FROM = { check_variable = { wif_gp_loyalty < 25 } } }
        }
    }

    wif_gp_managed_retreat_@S@ = {
        icon = generic_break_treaty
        cost = 25
        target_trigger = { wif_gp_root_is_from_patron = yes }
        visible = {
            wif_gp_is_global = yes
            check_variable = { wif_gp_slot = @S@ }
            has_country_flag = wif_gp_strain
        }
        complete_effect = {
            set_country_flag = { flag = wif_gp_retreat_shield value = 1 days = 120 }
            add_to_variable = { wif_gp_cred = -5 }
            clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
            if = {
                limit = { FROM = { is_subject_of = ROOT } }
                end_puppet = FROM
            }
            FROM = {
                if = { limit = { is_in_faction_with = ROOT } leave_faction = yes }
                set_variable = { wif_gp_inf_@S@ = 45 }
                set_variable = { wif_gp_fav_@S@ = 60 }
            }
            custom_effect_tooltip = wif_gp_managed_retreat_tt
        }
        ai_will_do = {
            base = 0
            modifier = {
                add = 6
                has_country_flag = wif_gp_crisis
                FROM = {
                    check_variable = { wif_gp_loyalty < 20 }
                    wif_gp_is_proxy_size = yes
                }
            }
        }
    }
''', S=s)

    # Reform the bloc, call on the bloc
    t += '''
    wif_gp_reform_bloc = {
        icon = generic_speech
        cost = 200
        days_re_enable = 365
        visible = { wif_gp_is_global = yes has_country_flag = wif_gp_strain }
        complete_effect = {
            random_list = {
                70 = {
                    set_country_flag = { flag = wif_gp_reformed value = 1 days = 90 }
                    custom_effect_tooltip = wif_gp_reform_good_tt
                }
                30 = {
                    add_to_variable = { wif_gp_cohesion = -15 }
                    add_to_variable = { wif_gp_cred = -10 }
                    clamp_variable = { var = wif_gp_cohesion min = 0 max = 100 }
                    clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
                    custom_effect_tooltip = wif_gp_reform_bad_tt
                }
            }
        }
        ai_will_do = {
            base = 0
            modifier = { add = 5 has_country_flag = wif_gp_crisis has_political_power > 220 }
        }
    }

    wif_gp_call_on_bloc = {
        icon = generic_civil_support
        cost = 25
        days_re_enable = 180
        visible = {
            wif_gp_is_global = yes
            has_country_flag = wif_gp_strain
            is_faction_leader = yes
        }
        complete_effect = {
            every_country = {
                limit = { is_in_faction_with = ROOT NOT = { tag = ROOT } }
                set_variable = { wif_gp_ev_power = ROOT }
                country_event = { id = wif_gp.44 }
            }
        }
        ai_will_do = {
            base = 0
            modifier = { add = 6 has_country_flag = wif_gp_crisis }
        }
    }
'''

    # Proxy-war decisions (patron targets its own main proxy / rival patron)
    t += '''
    wif_gp_widen_war = {
        icon = generic_army_support
        cost = 50
        target_trigger = {
            FROM = {
                wif_gp_is_proxy_size = yes
                has_country_flag = wif_gp_has_patron
                var:wif_gp_patron = { tag = ROOT }
                has_war = no
                wif_gp_immune_spirit = no
                any_neighbor_country = {
                    has_country_flag = wif_gp_px_main
                    any_country = {
                        has_country_flag = wif_gp_px_main
                        check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                        var:wif_gp_px_patron = { tag = ROOT }
                    }
                }
            }
        }
        visible = { wif_gp_is_global = yes }
        complete_effect = {
            FROM = {
                random_neighbor_country = {
                    limit = {
                        has_country_flag = wif_gp_px_main
                        any_country = {
                            has_country_flag = wif_gp_px_main
                            check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                            var:wif_gp_px_patron = { tag = ROOT }
                        }
                    }
                    PREV = { set_variable = { wif_gp_px_id = PREV.wif_gp_px_id } }
                    random_country = {
                        limit = {
                            has_country_flag = wif_gp_px_main
                            check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                            var:wif_gp_px_patron = { tag = ROOT }
                        }
                        set_variable = { global.wif_gp_tmp_side = wif_gp_px_side }
                    }
                }
                set_variable = { wif_gp_px_side = global.wif_gp_tmp_side }
                set_variable = { wif_gp_px_patron = ROOT }
                set_country_flag = wif_gp_px_widened
                random_country = {
                    limit = {
                        has_country_flag = wif_gp_px_main
                        check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                        NOT = { check_variable = { wif_gp_px_side = PREV.wif_gp_px_side } }
                    }
                    PREV = { declare_war_on = { target = PREV type = annex_everything } }
                }
            }
            custom_effect_tooltip = wif_gp_widen_tt
        }
        ai_will_do = {
            base = 0
            modifier = {
                add = 5
                has_political_power > 100
                any_country = {
                    has_country_flag = wif_gp_px_main
                    var:wif_gp_px_patron = { tag = ROOT }
                    OR = {
                        surrender_progress > 0.15
                        any_country = {
                            has_country_flag = wif_gp_px_widened
                            check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                            NOT = { check_variable = { wif_gp_px_side = PREV.wif_gp_px_side } }
                        }
                    }
                }
            }
        }
    }

    wif_gp_halt_war = {
        icon = generic_political_address
        cost = 25
        days_re_enable = 60
        target_trigger = {
            FROM = {
                wif_gp_is_global = yes
                NOT = { tag = ROOT }
            }
            any_country = {
                has_country_flag = wif_gp_px_main
                var:wif_gp_px_patron = { tag = ROOT }
                any_country = {
                    has_country_flag = wif_gp_px_main
                    check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                    var:wif_gp_px_patron = { tag = FROM }
                }
            }
        }
        visible = { wif_gp_is_global = yes }
        complete_effect = {
            random_country = {
                limit = {
                    has_country_flag = wif_gp_px_main
                    var:wif_gp_px_patron = { tag = ROOT }
                    any_country = {
                        has_country_flag = wif_gp_px_main
                        check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                        var:wif_gp_px_patron = { tag = FROM }
                    }
                }
                FROM = { set_variable = { wif_gp_ev_px = PREV.wif_gp_px_id } }
            }
            FROM = {
                set_variable = { wif_gp_ev_power = ROOT }
                country_event = { id = wif_gp.54 }
            }
            add_to_variable = { wif_gp_cred = -8 }
            clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
            custom_effect_tooltip = wif_gp_halt_tt
        }
        ai_will_do = {
            base = 0
            modifier = {
                add = 5
                check_variable = { wif_gp_cred > 20 }
                any_country = {
                    has_country_flag = wif_gp_px_main
                    var:wif_gp_px_patron = { tag = ROOT }
                    surrender_progress > 0.3
                }
            }
        }
    }

    wif_gp_escalate_war = {
        icon = generic_prepare_civil_war
        cost = 100
        target_trigger = {
            FROM = {
                has_country_flag = wif_gp_px_main
                var:wif_gp_px_patron = { tag = ROOT }
                surrender_progress > 0.3
                any_country = {
                    has_country_flag = wif_gp_px_widened
                    check_variable = { wif_gp_px_id = PREV.wif_gp_px_id }
                }
            }
        }
        visible = { wif_gp_is_global = yes }
        complete_effect = {
            set_variable = { wif_gp_ev_px = FROM.wif_gp_px_id }
            wif_gp_px_escalate = yes
        }
        ai_will_do = {
            base = 0
            modifier = {
                add = 2
                check_variable = { wif_gp_cred > 60 }
                NOT = { has_country_flag = wif_gp_strain }
                has_war = no
            }
        }
    }
'''

    # Send a volunteer corps (player route for civil wars and proxies)
    t += '''
    wif_gp_send_corps = {
        icon = generic_army_support
        cost = 50
        days_re_enable = 180
        target_trigger = {
            FROM = {
                has_war = yes
                OR = {
                    AND = { has_variable = wif_gp_px_patron var:wif_gp_px_patron = { tag = ROOT } }
                    AND = { has_variable = wif_gp_cw_patron var:wif_gp_cw_patron = { tag = ROOT } }
                }
            }
        }
        visible = { wif_gp_is_global = yes is_ai = no }
        complete_effect = {
            FROM = {
                set_variable = { wif_gp_vol_from = ROOT }
                country_event = { id = wif_gp.27 }
            }
            custom_effect_tooltip = wif_gp_corps_tt
        }
        ai_will_do = { base = 0 }
    }
}

wif_gp_nuclear_category = {
}

wif_gp_nam_category = {
    wif_gp_nam_found = {
        icon = generic_political_rally
        cost = 100
        visible = { NOT = { has_global_flag = wif_gp_nam_exists } }
        available = {
            wif_gp_nam_eligible = yes
            check_variable = { global.wif_gp_global_count > 1 }
            any_country = {
                NOT = { tag = ROOT }
                wif_gp_nam_eligible = yes
            }
        }
        complete_effect = {
            set_global_flag = wif_gp_nam_exists
            set_global_flag = { flag = wif_gp_nam_grace value = 1 days = 365 }
            set_global_flag = { flag = wif_gp_nam_summit_cd value = 1 days = 1200 }
            set_variable = { global.wif_gp_nam_leader = ROOT }
            add_ideas = wif_gp_nam_member_idea
            news_event = { id = wif_gp.80 days = 1 }
            hidden_effect = {
                every_country = {
                    limit = { wif_gp_nam_eligible = yes NOT = { tag = ROOT } }
                    country_event = { id = wif_gp.81 days = 3 }
                }
            }
        }
        ai_will_do = {
            base = 0
            modifier = { add = 3 has_government = neutrality }
            modifier = { add = 2 has_government = democratic }
        }
    }

    wif_gp_nam_join = {
        icon = generic_civil_support
        cost = 50
        visible = {
            has_global_flag = wif_gp_nam_exists
            wif_gp_nam_member = no
        }
        available = { wif_gp_nam_eligible = yes }
        complete_effect = { add_ideas = wif_gp_nam_member_idea }
        ai_will_do = {
            base = 0
            modifier = { add = 2 has_government = neutrality }
            modifier = { add = 1 has_government = democratic }
        }
    }

    wif_gp_nam_leave = {
        icon = generic_break_treaty
        cost = 0
        visible = { wif_gp_nam_member = yes }
        complete_effect = { remove_ideas = wif_gp_nam_member_idea }
        ai_will_do = { base = 0 }
    }
}
'''
    # Gamble cap var: claim_cap + 1
    return t


# ---------------------------------------------------------------------------
# Scripted localisation
# ---------------------------------------------------------------------------
def gen_scripted_loc():
    t = HEADER
    t += 'defined_text = {\n    name = GetWifGpTier\n'
    for n in [4, 3, 2, 1, 0]:
        t += f'    text = {{ trigger = {{ check_variable = {{ wif_gp_tier = {n} }} }} localization_key = wif_gp_tier_name_{n} }}\n'
    t += '}\n\n'
    t += '''defined_text = {
    name = GetWifGpStage
    text = { trigger = { has_country_flag = wif_gp_crisis } localization_key = wif_gp_stage_crisis }
    text = { trigger = { has_country_flag = wif_gp_strain } localization_key = wif_gp_stage_strain }
    text = { localization_key = wif_gp_stage_stable }
}

defined_text = {
    name = GetWifGpRival
    text = { trigger = { has_variable = wif_gp_rival } localization_key = wif_gp_rival_named }
    text = { localization_key = wif_gp_rival_none }
}

defined_text = {
    name = GetWifGpDoctrine
    text = { trigger = { check_variable = { wif_gp_doctrine = 4 } } localization_key = wif_gp_doctrine_4 }
    text = { trigger = { check_variable = { wif_gp_doctrine = 3 } } localization_key = wif_gp_doctrine_3 }
    text = { trigger = { check_variable = { wif_gp_doctrine = 2 } } localization_key = wif_gp_doctrine_2 }
    text = { localization_key = wif_gp_doctrine_1 }
}

defined_text = {
    name = GetWifGpClaims
'''
    # list claimed regions: one text per region is not combinable; show count + a few
    t += '    text = { localization_key = wif_gp_claims_count }\n}\n\n'
    t += 'defined_text = {\n    name = GetWifGpClaimList\n'
    # Can't concatenate; emit per-region lines via separate defined_texts
    t += '    text = { localization_key = wif_gp_empty }\n}\n\n'
    for k, _n, _s in REGIONS:
        t += f'''defined_text = {{
    name = GetWifGpClaim_{k}
    text = {{ trigger = {{ has_country_flag = wif_gp_claim_{k} }} localization_key = wif_gp_claimline_{k} }}
    text = {{ localization_key = wif_gp_empty }}
}}

'''
    t += '''defined_text = {
    name = GetWifGpNamLeader
    text = { trigger = { has_global_flag = wif_gp_nam_exists } localization_key = wif_gp_nam_leader_line }
    text = { localization_key = wif_gp_nam_none }
}
'''
    return t


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------
def news(eid, title_key=None, body=''):
    return f'''
news_event = {{
    id = wif_gp.{eid}
    title = wif_gp.{eid}.t
    desc = wif_gp.{eid}.d
    picture = GFX_news_event_generic_read_write
    major = yes
    is_triggered_only = yes
{body}    option = {{ name = wif_gp.{eid}.a }}
}}
'''


def gen_events():
    t = HEADER + 'add_namespace = wif_gp\n'
    # News events (sent once from the acting country)
    for eid in [1, 2, 4, 6, 41, 43, 51, 57, 58, 80, 82, 83, 85] + [70 + n for n in range(len(RACES))]:
        t += news(eid)

    t += '''
# Fallen Power: how to bear the loss.
country_event = {
    id = wif_gp.3
    title = wif_gp.3.t
    desc = wif_gp.3.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = {
        name = wif_gp.3.a
        ai_chance = { base = 40 modifier = { factor = 2 has_government = fascism } }
        add_timed_idea = { idea = wif_gp_lost_greatness_idea days = 3650 }
    }
    option = {
        name = wif_gp.3.b
        ai_chance = { base = 60 modifier = { factor = 2 has_government = democratic } }
        add_timed_idea = { idea = wif_gp_new_role_idea days = 365 }
    }
}

# Overshadowed.
country_event = {
    id = wif_gp.5
    title = wif_gp.5.t
    desc = wif_gp.5.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = wif_gp.5.a }
}

# Growing Superpower.
country_event = {
    id = wif_gp.7
    title = wif_gp.7.t
    desc = wif_gp.7.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = wif_gp.7.a }
}

# Rival chosen.
country_event = {
    id = wif_gp.10
    title = wif_gp.10.t
    desc = wif_gp.10.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    trigger = { is_ai = no }
    option = { name = wif_gp.10.a }
}

# Influence: a foreign-backed party demands power (human target).
country_event = {
    id = wif_gp.20
    title = wif_gp.20.t
    desc = wif_gp.20.d
    picture = GFX_report_event_generic_rally
    is_triggered_only = yes
    option = {
        name = wif_gp.20.a
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ check_variable = {{ wif_gp_ev_slot = {s} }} }}
            wif_gp_set_gov_slot_{s} = yes
        }}
'''
    t += '''    }
    option = {
        name = wif_gp.20.b
        add_stability = -0.1
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ check_variable = {{ wif_gp_ev_slot = {s} }} }}
            add_to_variable = {{ wif_gp_inf_{s} = -10 }}
            clamp_variable = {{ var = wif_gp_inf_{s} min = 0 max = 100 }}
        }}
'''
    t += '''    }
}

# Influence: invitation into the bloc (human target).
country_event = {
    id = wif_gp.21
    title = wif_gp.21.t
    desc = wif_gp.21.d
    picture = GFX_report_event_generic_sign_treaty1
    is_triggered_only = yes
    option = {
        name = wif_gp.21.a
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ check_variable = {{ wif_gp_ev_slot = {s} }} }}
            wif_gp_join_slot_{s} = yes
        }}
'''
    t += '''    }
    option = {
        name = wif_gp.21.b
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ check_variable = {{ wif_gp_ev_slot = {s} }} }}
            add_to_variable = {{ wif_gp_fav_{s} = -15 }}
            clamp_variable = {{ var = wif_gp_fav_{s} min = 0 max = 100 }}
        }}
'''
    t += '''    }
}

# Civil war: a human patron decides whether to back its side.
country_event = {
    id = wif_gp.26
    title = wif_gp.26.t
    desc = wif_gp.26.d
    picture = GFX_report_event_generic_rally
    is_triggered_only = yes
    option = {
        name = wif_gp.26.a
        var:wif_gp_ev_target = {
            set_variable = { wif_gp_vol_from = ROOT }
            country_event = { id = wif_gp.27 }
        }
    }
    option = {
        name = wif_gp.26.b
        var:wif_gp_ev_target = {
            set_country_flag = { flag = wif_gp_supported value = 1 days = 120 }
            PREV = { send_equipment = { equipment = infantry_equipment amount = 3000 target = PREV } }
        }
    }
    option = {
        name = wif_gp.26.c
        add_to_variable = { wif_gp_cred = -5 }
        clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
    }
}

# Hidden: a volunteer corps arrives. ROOT = recipient, wif_gp_vol_from = patron.
country_event = {
    id = wif_gp.27
    title = wif_gp.27.t
    desc = wif_gp.27.d
    picture = GFX_report_event_generic_rally
    is_triggered_only = yes
    hidden = yes
    immediate = {
        if = {
            limit = { NOT = { has_template = "Volunteer Corps" } }
            division_template = {
                name = "Volunteer Corps"
                regiments = {
                    infantry = { x = 0 y = 0 }
                    infantry = { x = 0 y = 1 }
                    infantry = { x = 0 y = 2 }
                    infantry = { x = 1 y = 0 }
                    infantry = { x = 1 y = 1 }
                    infantry = { x = 1 y = 2 }
                    artillery_brigade = { x = 2 y = 0 }
                }
                support = {
                    engineer = { x = 0 y = 0 }
                    recon = { x = 0 y = 1 }
                }
            }
        }
        if = {
            limit = { capital_scope = { is_controlled_by = ROOT } }
            capital_scope = {
                create_unit = {
                    division = "name = \\"Volunteer Corps\\" division_template = \\"Volunteer Corps\\" start_experience_factor = 0.3 start_equipment_factor = 1.0"
                    owner = ROOT
                    count = 3
                }
            }
        }
        else = {
            random_controlled_state = {
                create_unit = {
                    division = "name = \\"Volunteer Corps\\" division_template = \\"Volunteer Corps\\" start_experience_factor = 0.3 start_equipment_factor = 1.0"
                    owner = ROOT
                    count = 3
                }
            }
        }
        set_country_flag = { flag = wif_gp_supported value = 1 days = 120 }
        var:wif_gp_vol_from = {
            add_manpower = -30000
            send_equipment = { equipment = infantry_equipment amount = 1500 target = ROOT }
        }
        log = "WiF GP: [?ROOT.wif_gp_vol_from.GetName] sent a volunteer corps to [Root.GetName]"
    }
}

# A sphere member was attacked (human patron).
country_event = {
    id = wif_gp.30
    title = wif_gp.30.t
    desc = wif_gp.30.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = wif_gp.30.a }
}

# Test of Resolve. ROOT = probed Global Power, wif_gp_ev_power = prober,
# wif_gp_ev_target = the probed client.
country_event = {
    id = wif_gp.31
    title = wif_gp.31.t
    desc = wif_gp.31.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = {
        name = wif_gp.31.a
        ai_chance = {
            base = 60
            modifier = { factor = 0.2 has_political_power < 60 }
            modifier = { factor = 0.5 has_country_flag = wif_gp_strain }
        }
        add_political_power = -50
        random_list = {
            70 = {
                add_to_variable = { wif_gp_cred = 8 }
                var:wif_gp_ev_power = { add_to_variable = { wif_gp_cred = -5 } clamp_variable = { var = wif_gp_cred min = 0 max = 100 } }
                custom_effect_tooltip = wif_gp_tor_win_tt
            }
            30 = {
                add_to_variable = { wif_gp_cred = 3 }
                var:wif_gp_ev_target = { set_country_flag = { flag = wif_gp_border_tension value = 1 days = 365 } }
                custom_effect_tooltip = wif_gp_tor_escalate_tt
            }
        }
        clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
    }
    option = {
        name = wif_gp.31.b
        ai_chance = { base = 40 }
        add_to_variable = { wif_gp_cred = -10 }
        clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
        var:wif_gp_ev_power = {
            add_to_variable = { wif_gp_cred = 5 }
            clamp_variable = { var = wif_gp_cred min = 0 max = 100 }
        }
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ var:wif_gp_ev_power = {{ check_variable = {{ wif_gp_slot = {s} }} }} }}
            var:wif_gp_ev_target = {{
                add_to_variable = {{ wif_gp_inf_{s} = 10 }}
                clamp_variable = {{ var = wif_gp_inf_{s} min = 0 max = 100 }}
            }}
        }}
'''
    t += '''    }
}

# Strain.
country_event = {
    id = wif_gp.40
    title = wif_gp.40.t
    desc = wif_gp.40.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = wif_gp.40.a }
}

# The sphere holds.
country_event = {
    id = wif_gp.42
    title = wif_gp.42.t
    desc = wif_gp.42.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = wif_gp.42.a }
}

# Call on the Bloc: a faction member is asked for help. wif_gp_ev_power = leader.
country_event = {
    id = wif_gp.44
    title = wif_gp.44.t
    desc = wif_gp.44.d
    picture = GFX_report_event_generic_sign_treaty1
    is_triggered_only = yes
    option = {
        name = wif_gp.44.a
        ai_chance = { base = 70 modifier = { factor = 0.3 has_political_power < 60 } }
        add_political_power = -50
        var:wif_gp_ev_power = {
            add_to_variable = { wif_gp_cohesion = 10 }
            clamp_variable = { var = wif_gp_cohesion min = 0 max = 100 }
        }
    }
    option = {
        name = wif_gp.44.b
        ai_chance = { base = 30 }
'''
    for s in SLOTS:
        t += f'''        if = {{
            limit = {{ var:wif_gp_ev_power = {{ check_variable = {{ wif_gp_slot = {s} }} }} }}
            add_to_variable = {{ wif_gp_fav_{s} = -10 }}
            clamp_variable = {{ var = wif_gp_fav_{s} min = 0 max = 100 }}
        }}
'''
    t += '''    }
}

# A member left our sphere (human patron). wif_gp_ev_target = the member.
country_event = {
    id = wif_gp.46
    title = wif_gp.46.t
    desc = wif_gp.46.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = { name = wif_gp.46.a }
}

# Proxy war: a border clash. ROOT = aggressor, wif_gp_ev_target = neighbour.
country_event = {
    id = wif_gp.50
    title = wif_gp.50.t
    desc = wif_gp.50.d
    picture = GFX_report_event_generic_rally
    is_triggered_only = yes
    option = {
        name = wif_gp.50.a
        ai_chance = {
            base = 30
            modifier = { add = 50 check_variable = { wif_gp_score > wif_gp_ev_tscore } }
        }
        wif_gp_start_proxy_war = yes
    }
    option = {
        name = wif_gp.50.b
        ai_chance = { base = 30 }
        clr_country_flag = wif_gp_border_tension
        var:wif_gp_ev_target = { clr_country_flag = wif_gp_border_tension }
    }
}

# Halt proposal. ROOT = asked patron, wif_gp_ev_power = asking patron,
# wif_gp_ev_px = war id.
country_event = {
    id = wif_gp.54
    title = wif_gp.54.t
    desc = wif_gp.54.d
    picture = GFX_report_event_generic_sign_treaty1
    is_triggered_only = yes
    option = {
        name = wif_gp.54.a
        ai_chance = {
            base = 30
            modifier = {
                add = 50
                any_country = {
                    has_country_flag = wif_gp_px_main
                    check_variable = { wif_gp_px_id = ROOT.wif_gp_ev_px }
                    var:wif_gp_px_patron = { tag = ROOT }
                    surrender_progress > 0.15
                }
            }
        }
        set_variable = { global.wif_gp_cur_id = wif_gp_ev_px }
        set_variable = { global.wif_gp_px_flip = 1 }
        wif_gp_end_proxy_war = yes
        var:wif_gp_ev_power = { set_country_flag = wif_gp_halt_accepted country_event = { id = wif_gp.55 } }
        news_event = { id = wif_gp.57 days = 1 }
    }
    option = {
        name = wif_gp.54.b
        ai_chance = { base = 40 }
        var:wif_gp_ev_power = { clr_country_flag = wif_gp_halt_accepted country_event = { id = wif_gp.55 } }
    }
}

country_event = {
    id = wif_gp.55
    title = wif_gp.55.t
    desc = {
        text = wif_gp.55.d_yes
        trigger = { has_country_flag = wif_gp_halt_accepted }
    }
    desc = {
        text = wif_gp.55.d_no
        trigger = { NOT = { has_country_flag = wif_gp_halt_accepted } }
    }
    picture = GFX_report_event_generic_sign_treaty1
    is_triggered_only = yes
    option = { name = wif_gp.55.a clr_country_flag = wif_gp_halt_accepted }
}

# A widened ally breaks. ROOT = its patron.
country_event = {
    id = wif_gp.56
    title = wif_gp.56.t
    desc = wif_gp.56.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    option = {
        name = wif_gp.56.a
        ai_chance = {
            base = 30
            modifier = { add = 50 check_variable = { wif_gp_cred < 30 } }
        }
        wif_gp_px_cut_losses = yes
    }
    option = {
        name = wif_gp.56.b
        ai_chance = {
            base = 40
            modifier = {
                add = 30
                any_country = {
                    has_country_flag = wif_gp_px_main
                    check_variable = { wif_gp_px_id = ROOT.wif_gp_ev_px }
                    var:wif_gp_px_patron = { tag = ROOT }
                    surrender_progress > 0.3
                }
            }
        }
        wif_gp_px_reach_out = yes
    }
    option = {
        name = wif_gp.56.c
        ai_chance = {
            base = 10
            modifier = { add = 30 check_variable = { wif_gp_cred > 60 } has_war = no NOT = { has_country_flag = wif_gp_strain } }
        }
        wif_gp_px_escalate = yes
    }
}

# Non-Aligned Movement: invitation. ROOT = eligible country.
country_event = {
    id = wif_gp.81
    title = wif_gp.81.t
    desc = wif_gp.81.d
    picture = GFX_report_event_generic_sign_treaty1
    is_triggered_only = yes
    trigger = { wif_gp_nam_eligible = yes has_global_flag = wif_gp_nam_exists }
    option = {
        name = wif_gp.81.a
        ai_chance = {
            base = 60
            modifier = { factor = 1.5 has_government = neutrality }
            modifier = { factor = 0.5 has_government = fascism }
        }
        add_ideas = wif_gp_nam_member_idea
    }
    option = {
        name = wif_gp.81.b
        ai_chance = { base = 40 }
    }
}

# Overstretched economy.
country_event = {
    id = wif_gp.90
    title = wif_gp.90.t
    desc = wif_gp.90.d
    picture = GFX_report_event_generic_factory
    is_triggered_only = yes
    option = { name = wif_gp.90.a }
}

# --- Debug (console): event wif_gp.990 runs the monthly pass now;
# event wif_gp.991 gives ROOT the Global Power requirements and 10 nukes.
country_event = {
    id = wif_gp.990
    title = wif_gp.990.t
    desc = wif_gp.990.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    immediate = { wif_gp_monthly = yes }
    option = { name = wif_gp.990.a }
}

country_event = {
    id = wif_gp.991
    title = wif_gp.991.t
    desc = wif_gp.991.d
    picture = GFX_report_event_generic_read_write
    is_triggered_only = yes
    immediate = {
        set_technology = { nukes = 1 advanced_large_airframe = 1 popup = no }
        add_nuclear_bombs = 10
        set_variable = { wif_gp_cand_months = 3 }
    }
    option = { name = wif_gp.991.a }
}
'''
    return t


# ---------------------------------------------------------------------------
# Localisation
# ---------------------------------------------------------------------------
def gen_loc():
    L = {}
    # Tiers & stages
    L.update({
        'wif_gp_tier_name_4': 'Global Power', 'wif_gp_tier_name_3': 'Growing Superpower',
        'wif_gp_tier_name_2': 'Great Power', 'wif_gp_tier_name_1': 'Regional Power', 'wif_gp_tier_name_0': 'Minor Power',
        'wif_gp_stage_stable': '§GStable§!', 'wif_gp_stage_strain': '§YStrained§!', 'wif_gp_stage_crisis': '§RIn Crisis§!',
        'wif_gp_rival_named': '[?ROOT.wif_gp_rival.GetName]', 'wif_gp_rival_none': 'none yet',
        'wif_gp_doctrine_1': '§YLast Resort§!', 'wif_gp_doctrine_2': '§OThreat Launch§!',
        'wif_gp_doctrine_3': '§RFirst Strike§!', 'wif_gp_doctrine_4': '§ROur Flames of Radiation Shall Purify the Planet§!',
        'wif_gp_claims_count': '[?ROOT.wif_gp_claims|0] of [?ROOT.wif_gp_claim_cap|0] we can carry',
        'wif_gp_empty': '', 'wif_gp_nam_none': 'The movement does not exist.',
        'wif_gp_nam_leader_line': 'Led by [?global.wif_gp_nam_leader.GetName], [?global.wif_gp_nam_count|0] members.',
        'wif_gp_bloc_faction': '[ROOT.GetAdjective] Bloc',
        'wif_gp_secession_autonomy': 'Foreign-backed secessionists',
    })
    for k, n, _s in REGIONS:
        L[f'wif_gp_claimline_{k}'] = f'\\n - {n}'
    claim_list = ''.join(f'[ROOT.GetWifGpClaim_{k}]' for k, _n, _s in REGIONS)

    # Ideas
    L.update({
        'wif_gp_tier_global': 'Weltmacht',
        'wif_gp_tier_global_desc': 'We are one of the few powers that can end the world. Every capital watches what we do, and every small nation in our sphere expects us to keep our word. Our commitments abroad cost us at home.',
        'wif_gp_tier_growing': 'Growing Superpower',
        'wif_gp_tier_growing_desc': 'We hold the bomb and lead our own bloc. The Global Powers can no longer buy our politicians - we are strong enough to stand on our own and rise.',
        'wif_gp_tier_great': 'Great Power',
        'wif_gp_tier_great_desc': 'We are one of the great nations of the world, though not yet one of its masters.',
        'wif_gp_tier_regional': 'Regional Power',
        'wif_gp_tier_regional_desc': 'In our corner of the world we matter. Further afield, the great powers court us - or try to buy us.',
        'wif_gp_overshadowed_idea': 'In the Shadow of Giants',
        'wif_gp_overshadowed_idea_desc': 'Two stronger Global Powers stand in our own alliance. Beside them we look small, and the world treats us that way.',
        'wif_gp_lost_greatness_idea': 'Lost Greatness',
        'wif_gp_lost_greatness_idea_desc': 'We were a Global Power, and we will be again. Those who took what was ours will answer for it.',
        'wif_gp_new_role_idea': 'A New Role in the World',
        'wif_gp_new_role_idea_desc': 'We have accepted that our days as a world power are over. The relief is palpable.',
        'wif_gp_sphere_holds_idea': 'The Sphere Holds',
        'wif_gp_sphere_holds_idea_desc': 'The crisis is over. Our allies stayed, and the world saw it.',
        'wif_gp_overstretched_idea': 'Overstretched Economy',
        'wif_gp_overstretched_idea_desc': 'For two years our factories have built guns instead of goods. The arms race is bleeding the nation dry.',
        'wif_gp_cannot_fall_behind_idea': 'We Cannot Fall Behind',
        'wif_gp_cannot_fall_behind_idea_desc': 'A rival has beaten us to a milestone of the new age. Our scientists are told to close the gap at any cost.',
        'wif_gp_nam_member_idea': 'Non-Aligned',
        'wif_gp_nam_member_idea_desc': 'We belong to neither bloc. Influence from the Global Powers works at half strength on us and fades twice as fast, and an attack on any member is an attack on the movement\'s conscience.',
        'wif_gp_nam_summit_idea': 'Non-Aligned Summit',
        'wif_gp_nam_summit_idea_desc': 'The movement has met again and spoken with one voice.',
    })

    # Categories
    L.update({
        'wif_gp_weltpolitik_category': 'Weltpolitik',
        'wif_gp_weltpolitik_category_desc': (
            'Standing: §Y[ROOT.GetWifGpTier]§! - power score [?ROOT.wif_gp_score|0]\\n'
            'Credibility: §Y[?ROOT.wif_gp_cred|0]§!/100\\n'
            'Sphere cohesion: [?ROOT.wif_gp_cohesion|0]/100 ([ROOT.GetWifGpStage])\\n'
            'Rival: §Y[ROOT.GetWifGpRival]§!\\n'
            'Claimed regions: [ROOT.GetWifGpClaims]' + claim_list + '\\n\\n'
            'Claiming a region costs credibility; each nation that joins our bloc earns it back. '
            'Influence campaigns drift a nation towards our ideology, at 40 influence its government can fall our way, '
            'and at 60 a nation of our ideology joins our bloc. Two blocs pulling one nation in different directions can tear it apart in civil war.'),
        'wif_gp_nuclear_category': 'Nuclear Command',
        'wif_gp_nuclear_category_desc': (
            'Nuclear doctrine: [ROOT.GetWifGpDoctrine]\\n'
            'Warheads ready: [?ROOT.num_of_nukes|0]\\n\\n'
            'Our doctrine decides when our commanders release the bomb. It is set by the state, not by a minister, and cannot be changed by decree.\\n\\n'
            '§YLast Resort§!: only if we face destruction (70% surrender) or an ally in our faction or sphere has been struck.\\n'
            '§OThreat Launch§!: also when we reach 20% surrender, or four of our allies and puppets have fallen.\\n'
            '§RFirst Strike§!: against a nuclear enemy, at once - silos and airfields first, to kill their second strike.\\n'
            '§ROur Flames of Radiation Shall Purify the Planet§!: everything, everywhere, as much as possible.\\n\\n'
            'A struck state loses 8% of its people, a rocket site, and its airfields stay grounded while the fallout lasts.'),
        'wif_gp_nam_category': 'The Non-Aligned Movement',
        'wif_gp_nam_category_desc': '[ROOT.GetWifGpNamLeader]\\n\\nNations that refuse both blocs can stand together. Members are harder to influence, take aid from anyone, and protest together when a Global Power attacks one of them.',
    })

    # Decisions
    for k, n, _s in REGIONS:
        L[f'wif_gp_claim_{k}'] = f'Proclaim a Doctrine for {n}'
        L[f'wif_gp_claim_{k}_desc'] = f'Declare {n} part of our sphere. We will be expected to defend it.'
        L[f'wif_gp_abandon_{k}'] = f'Withdraw from {n}'
        L[f'wif_gp_abandon_{k}_desc'] = f'We can no longer carry {n}. Better to step back in good order than be pushed out.'
    for s in SLOTS:
        L[f'wif_gp_influence_{s}'] = 'Influence Campaign in [From.GetName]'
        L[f'wif_gp_influence_{s}_desc'] = 'Newspapers, scholarships, party funds and quiet advisers for six months.'
        L[f'wif_gp_fund_dissidents_{s}'] = 'Fund Dissidents in [From.GetName]'
        L[f'wif_gp_fund_dissidents_{s}_desc'] = 'Our rival\'s client has malcontents. Give them money and a printing press.'
        L[f'wif_gp_back_secessionists_{s}'] = 'Back Secessionists in [From.GetName]'
        L[f'wif_gp_back_secessionists_{s}_desc'] = 'Help this puppet of our rival remember that it was once free.'
        L[f'wif_gp_stoke_tensions_{s}'] = 'Stoke Border Tensions with [From.GetName]'
        L[f'wif_gp_stoke_tensions_{s}_desc'] = 'Incidents on the border make a proxy war far more likely.'
        L[f'wif_gp_probe_{s}'] = 'Test the Resolve of [From.GetName]\'s Patron'
        L[f'wif_gp_probe_{s}_desc'] = 'Lean on our rival\'s client and see whether our rival dares to stand firm.'
        L[f'wif_gp_subsidies_{s}'] = 'Emergency Subsidies for [From.GetName]'
        L[f'wif_gp_subsidies_{s}_desc'] = 'Money and grain buy loyalty for a while.'
        L[f'wif_gp_crackdown_{s}'] = 'Crack Down in [From.GetName]'
        L[f'wif_gp_crackdown_{s}_desc'] = 'Force them to stay. They will not forgive us.'
        L[f'wif_gp_managed_retreat_{s}'] = 'Let [From.GetName] Go'
        L[f'wif_gp_managed_retreat_{s}_desc'] = 'Release it on our terms, before it tears itself away, and buy time for the rest of the sphere.'
    L.update({
        'wif_gp_reform_bloc': 'Reform the Bloc',
        'wif_gp_reform_bloc_desc': 'Loosen the reins across the whole sphere. It may save the bloc - or show everyone how weak we have become.',
        'wif_gp_call_on_bloc': 'Call on the Bloc',
        'wif_gp_call_on_bloc_desc': 'Ask our faction to share the burden of holding the sphere together.',
        'wif_gp_widen_war': 'Bring [From.GetName] into the Proxy War',
        'wif_gp_widen_war_desc': 'A neighbouring member of our bloc will join our client\'s war. Our rival may answer in kind.',
        'wif_gp_halt_war': 'Propose a Ceasefire to [From.GetName]',
        'wif_gp_halt_war_desc': 'Ask our rival to halt the proxy war. If they agree, every state ends with whoever occupies it. Asking costs us credibility.',
        'wif_gp_escalate_war': 'Intervene Directly for [From.GetName]',
        'wif_gp_escalate_war_desc': 'Our client is losing a widened war. We and our whole alliance enter it directly - and the other bloc will do the same.',
        'wif_gp_send_corps': 'Send a Volunteer Corps to [From.GetName]',
        'wif_gp_send_corps_desc': 'Three divisions of volunteers, equipped from our stocks.',
        'wif_gp_nam_found': 'Call the Non-Aligned Conference',
        'wif_gp_nam_found_desc': 'Invite every nation that belongs to neither bloc to stand together.',
        'wif_gp_nam_join': 'Join the Non-Aligned Movement',
        'wif_gp_nam_join_desc': 'Neither bloc will own us.',
        'wif_gp_nam_leave': 'Leave the Non-Aligned Movement',
        'wif_gp_nam_leave_desc': 'We no longer need the movement.',
    })
    # Tooltips
    L.update({
        'wif_gp_claim_tt': 'Unlocks influence campaigns in nations whose capital lies in this region.\\nEvery claimed region costs §R2%§! consumer goods.',
        'wif_gp_influence_tt': 'For §Y180§! days: §G+4§! influence a month (halved in the Non-Aligned Movement and in Great Powers).',
        'wif_gp_fund_dissidents_tt': 'Our ideology gains §G4%§! popularity; the target is §Rdestabilised§! for 180 days.',
        'wif_gp_stoke_tensions_tt': 'A proxy war on this border becomes §Rsix times§! as likely for a year.',
        'wif_gp_probe_tt': 'Our rival must stand firm or back down.',
        'wif_gp_crackdown_tt': 'The nation will §Rresent§! us for a year.',
        'wif_gp_managed_retreat_tt': 'Defections from our sphere are halved for 120 days and cost less credibility.',
        'wif_gp_reform_good_tt': '§G70%§!: the bloc rallies.', 'wif_gp_reform_bad_tt': '§R30%§!: reform reads as weakness.',
        'wif_gp_widen_tt': 'The war widens. Nobody outside the proxy war may join it.',
        'wif_gp_halt_tt': 'If accepted, every occupied state goes to its occupier and the war ends.',
        'wif_gp_corps_tt': 'Three divisions arrive; we lose §R30k§! manpower and 1,500 rifles.',
        'wif_gp_tor_win_tt': '§G70%§!: they blink.', 'wif_gp_tor_escalate_tt': '§R30%§!: they push back - the border heats up.',
    })

    # Events
    E = {
        1: ('The Atomic Age', '[ROOT.GetName] has become the world\'s first Global Power. With the bomb and the bombers to carry it, it can now strike any city on earth. Every other great power is drawing the same conclusion: it must have the bomb too.', 'A new age begins.'),
        2: ('A New Global Power', '[ROOT.GetName] has joined the ranks of the Global Powers. The balance of the world shifts again.', 'The club grows.'),
        4: ('The End of an Era', '[ROOT.GetName] is no longer counted among the Global Powers. Its allies are already looking elsewhere.', 'How the mighty fall.'),
        6: ('A Split in the Red World', 'Two communist powers now regard each other as their greatest rival. The workers of the world, it seems, are not united after all.', 'Comrades no more.'),
        41: ('A Sphere in Crisis', 'The sphere of [ROOT.GetName] is coming apart. Its clients are wavering, its rivals are circling, and every defection makes the next one more likely.', 'Will it hold?'),
        43: ('A Sphere Collapses', 'The sphere of [ROOT.GetName] has fallen apart. Its puppets are breaking away and it can no longer call itself a Global Power.', 'An empire ends.'),
        51: ('War by Proxy', '[ROOT.GetName] and its neighbour are at war - and behind each stands a Global Power. Nobody else may enter this war; their patrons can only send arms and volunteers.', 'Another small war in a cold world.'),
        57: ('The Guns Fall Silent', 'A proxy war has ended. The patrons count their gains and losses in credibility.', 'Until the next one.'),
        58: ('The Proxy War Escalates', '[ROOT.GetName] has intervened directly in a proxy war, bringing its whole alliance with it. The other bloc has answered. What was a small war is now a war between blocs.', 'The world holds its breath.'),
        80: ('The Non-Aligned Movement', '[ROOT.GetName] has called the nations that refuse both blocs to stand together. Neither side will find them easy to buy.', 'A third way.'),
        82: ('The Non-Aligned Summit', 'The Non-Aligned Movement has met again under [ROOT.GetName]. Its members speak with one voice.', 'Neither east nor west.'),
        83: ('The Movement Dissolves', 'Too few nations remain in the Non-Aligned Movement for it to mean anything. The blocs have won.', 'So much for the third way.'),
        85: ('Proliferation', '[ROOT.GetName] has built an atomic bomb of its own. The Global Powers are alarmed: the club is no longer exclusive.', 'Another finger on the trigger.'),
    }
    for n, (k, d, _t) in enumerate(RACES):
        E[70 + n] = (f'First to {d[4:] if d.startswith("the ") else d}',
                     f'[ROOT.GetName] is the first nation in the world to achieve {d}. Its prestige soars, and every other great power orders its scientists to close the gap.',
                     'History is made.')
    for eid, (tt, dd, aa) in E.items():
        assert eid in NEWS_IDS, eid
        dd = dd.replace('[ROOT.GetName]', f'[?global.wif_gp_n{eid}.GetName]')
        L[f'wif_gp.{eid}.t'] = tt
        L[f'wif_gp.{eid}.d'] = dd
        L[f'wif_gp.{eid}.a'] = aa
    L.update({
        'wif_gp.3.t': 'We Are No Longer a Global Power', 'wif_gp.3.d': 'The world no longer counts us among its masters. How we bear the loss will shape the decade.',
        'wif_gp.3.a': 'We will take back what is ours.', 'wif_gp.3.b': 'We accept our new role.',
        'wif_gp.5.t': 'In the Shadow of Giants', 'wif_gp.5.d': 'Two stronger Global Powers stand in our own alliance. Beside them the world no longer sees us as a Global Power. Only if one of them falls, or if we go our own way, can we stand among them again.',
        'wif_gp.5.a': 'Bitter, but true.',
        'wif_gp.7.t': 'A Growing Superpower', 'wif_gp.7.d': 'With the bomb in our arsenal and our own bloc behind us, we are counted among the rising powers of the world. No Global Power can buy our politicians now.',
        'wif_gp.7.a': 'Onward.',
        'wif_gp.10.t': 'Our Rival', 'wif_gp.10.d': 'Our strategists agree: the greatest threat to our position is [?ROOT.wif_gp_rival.GetName]. Every arms programme, every client and every crisis will now be measured against them.',
        'wif_gp.10.a': 'So be it.',
        'wif_gp.20.t': 'A Foreign-Backed Party Demands Power', 'wif_gp.20.d': 'Backed by [?ROOT.wif_gp_ev_power.GetName], a rival party has grown strong enough to demand the government. We can give way, or resist at the cost of unrest.',
        'wif_gp.20.a': 'Hand them the government.', 'wif_gp.20.b': 'Resist - whatever it costs.',
        'wif_gp.21.t': 'An Invitation from [?ROOT.wif_gp_ev_power.GetName]', 'wif_gp.21.d': '[?ROOT.wif_gp_ev_power.GetName] has courted us for years. Now it invites us to join its bloc.',
        'wif_gp.21.a': 'We accept.', 'wif_gp.21.b': 'We decline.',
        'wif_gp.26.t': 'War in [?ROOT.wif_gp_ev_target.GetName]', 'wif_gp.26.d': '[?ROOT.wif_gp_ev_target.GetName] is fighting for its life - in a civil war or a proxy war - and it looks to us. The whole world is watching whether we stand by our friends.',
        'wif_gp.26.a': 'Send a volunteer corps.', 'wif_gp.26.b': 'Send rifles, not men.', 'wif_gp.26.c': 'Stay out of it.',
        'wif_gp.27.t': 'Volunteers Arrive', 'wif_gp.27.d': 'A volunteer corps has arrived.',
        'wif_gp.30.t': '[?ROOT.wif_gp_ev_target.GetName] Has Been Attacked', 'wif_gp.30.d': 'A nation in our sphere has been attacked. If we do not join the war or send help within 60 days, the whole world will know what our word is worth.',
        'wif_gp.30.a': 'We will not forget.',
        'wif_gp.31.t': 'A Test of Resolve', 'wif_gp.31.d': '[?ROOT.wif_gp_ev_power.GetName] is leaning on [?ROOT.wif_gp_ev_target.GetName] - troops on the border, threats in the press. Everyone is waiting to see whether we stand firm.',
        'wif_gp.31.a': 'Stand firm.', 'wif_gp.31.b': 'Back down.',
        'wif_gp.40.t': 'Strain in Our Sphere', 'wif_gp.40.d': 'Our sphere is under strain. If cohesion keeps falling, our clients will start leaving us. Emergency measures are now available in the Weltpolitik menu.',
        'wif_gp.40.a': 'We must act.',
        'wif_gp.42.t': 'The Sphere Holds', 'wif_gp.42.d': 'The crisis is behind us. Our allies stayed, and the world saw it.',
        'wif_gp.42.a': 'As we always said they would.',
        'wif_gp.44.t': 'The Bloc Calls for Help', 'wif_gp.44.d': '[?ROOT.wif_gp_ev_power.GetName] asks its allies to help hold the sphere together.',
        'wif_gp.44.a': 'We will help.', 'wif_gp.44.b': 'We cannot spare anything.',
        'wif_gp.46.t': '[?ROOT.wif_gp_ev_target.GetName] Has Left Our Sphere', 'wif_gp.46.d': 'A nation that once looked to us no longer does. The world has noticed.',
        'wif_gp.46.a': 'A setback.',
        'wif_gp.50.t': 'Border Clash with [?ROOT.wif_gp_ev_target.GetName]', 'wif_gp.50.d': 'Shots have been exchanged on the border with [?ROOT.wif_gp_ev_target.GetName], a client of a rival bloc. Our generals say we can win a short war - and our patron would back us. Nobody else would be allowed to join.',
        'wif_gp.50.a': 'Strike first.', 'wif_gp.50.b': 'Seek a settlement.',
        'wif_gp.54.t': '[?ROOT.wif_gp_ev_power.GetName] Proposes a Ceasefire', 'wif_gp.54.d': '[?ROOT.wif_gp_ev_power.GetName] asks us to halt the proxy war between our clients. If we agree, every state goes to whoever occupies it now.',
        'wif_gp.54.a': 'Agree to halt the war.', 'wif_gp.54.b': 'Refuse.',
        'wif_gp.55.t': 'An Answer on the Ceasefire', 'wif_gp.55.d_yes': 'Our rival has agreed. The proxy war is over, along the current front.', 'wif_gp.55.d_no': 'Our rival has refused. The war goes on.',
        'wif_gp.55.a': 'Noted.',
        'wif_gp.56.t': '[?ROOT.wif_gp_ev_target.GetName] Is Broken', 'wif_gp.56.d': '[?ROOT.wif_gp_ev_target.GetName], which we brought into the proxy war, is collapsing. We must decide how this war ends.',
        'wif_gp.56.a': 'Cut our losses - let it go.', 'wif_gp.56.b': 'Reach out - divide our client and end it.', 'wif_gp.56.c': 'Escalate - we go in ourselves.',
        'wif_gp.81.t': 'The Non-Aligned Conference', 'wif_gp.81.d': '[?global.wif_gp_nam_leader.GetName] invites us to join the nations that refuse both blocs.',
        'wif_gp.81.a': 'We join.', 'wif_gp.81.b': 'We will go our own way.',
        'wif_gp.90.t': 'An Overstretched Economy', 'wif_gp.90.d': 'For two years our factories have built weapons rather than goods. The arms race is costing us at home.',
        'wif_gp.90.a': 'We cannot stop now.',
        'wif_gp.990.t': 'Debug: Global Power Pass', 'wif_gp.990.d': 'Ran the monthly global power pass.', 'wif_gp.990.a': 'OK',
        'wif_gp.991.t': 'Debug: Global Power Requirements', 'wif_gp.991.d': 'Granted nukes, the advanced large airframe and 10 bombs.', 'wif_gp.991.a': 'OK',
    })

    out = 'l_english:\n'
    for k, v in L.items():
        out += f' {k}:0 "{v}"\n'
    return out


# ---------------------------------------------------------------------------
# Special projects: vanilla copies with an AI push
# ---------------------------------------------------------------------------
def gen_special_projects():
    push = '''		modifier = {
			factor = 20 # WiF: Nuclear Ambition (tools/gen_global_power.py)
			ROOT = { has_country_flag = wif_gp_nuclear_ambition }
		}
'''
    for fname, projects in SP_PUSH.items():
        src = os.path.join(GAME, 'common', 'special_projects', 'projects', fname)
        with open(src, encoding='utf-8-sig') as f:
            text = f.read()
        nl = '\r\n' if '\r\n' in text else '\n'
        text = text.replace('\r\n', '\n')
        for p in projects:
            m = re.search(r'^' + p + r' = \{', text, re.M)
            assert m, p
            # the project's block ends at the next line that is exactly "}"
            end = re.search(r'^\}', text[m.end():], re.M).start() + m.end()
            block = text[m.start():end]
            if '\tai_will_do = {' in block:
                block = re.sub(r'(\n\tai_will_do = \{\n(\t\tbase = [^\n]*\n)?)', lambda mm: mm.group(1) + push, block, count=1)
            else:
                block = block.rstrip('\n') + '\n\n\tai_will_do = {\n\t\tbase = 1\n' + push + '\t}\n'
            text = text[:m.start()] + block + text[end:]
        header = (f'# WiF COPY of vanilla common/special_projects/projects/{fname} - written by\n'
                  '# tools/gen_global_power.py, which adds a Nuclear Ambition AI modifier to\n'
                  f'# {", ".join(projects)}. Re-run the generator after a game update.\n\n')
        path = os.path.join(MOD, 'common', 'special_projects', 'projects', fname)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write((header + text).replace('\n', nl))
        print('wrote', os.path.relpath(path, MOD))


NEWS_IDS = [1, 2, 4, 6, 41, 43, 51, 57, 58, 80, 82, 83, 85] + [70 + n for n in range(len(RACES))]


def news_actor(text):
    """A major news event shows ROOT as the reader, so every news event names
    its actor through global.wif_gp_n<id>, set just before it is sent."""
    return re.sub(r'news_event = \{ id = wif_gp\.(\d+) days = 1 \}',
                  lambda m: f'set_variable = {{ global.wif_gp_n{m.group(1)} = THIS }} '
                            f'news_event = {{ id = wif_gp.{m.group(1)} days = 1 }}', text)


def main():
    regions = state_regions()
    print(f'{len(regions)} states mapped to {len(REGIONS)} regions')
    write('common/scripted_triggers/wif_gp_triggers.txt', gen_triggers())
    write('common/scripted_effects/wif_gp_regions_auto.txt', gen_region_effects(regions))
    write('common/scripted_effects/wif_gp_effects.txt', news_actor(gen_effects()))
    write('common/on_actions/wif_gp_on_actions.txt', news_actor(gen_on_actions()))
    write('common/ideas/wif_gp_ideas.txt', gen_ideas())
    write('common/dynamic_modifiers/wif_gp_dynamic_modifiers.txt', gen_dynamic_modifiers())
    write('common/opinion_modifiers/wif_gp_opinion_modifiers.txt', gen_opinion_modifiers())
    write('common/ai_strategy/wif_gp_ai.txt', gen_ai())
    write('common/decisions/categories/wif_gp_categories.txt', gen_categories())
    write('common/decisions/wif_gp_decisions.txt', news_actor(gen_decisions()))
    write('common/scripted_localisation/wif_gp_scripted_loc.txt', gen_scripted_loc())
    write('events/wif_gp_events.txt', news_actor(gen_events()))
    write('localisation/english/wif_gp_l_english.yml', gen_loc(), bom=True)
    gen_special_projects()


if __name__ == '__main__':
    main()
