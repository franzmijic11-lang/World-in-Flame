-- Welt in Flammen define overrides.
-- Loaded after vanilla common/defines/00_defines.lua (alphabetical order), so
-- assignments here replace the stock values. Only list what actually changes.

-- Allow stability to fall to -100%. Vanilla clamps it at 0%.
--
-- Effects scale rather than plateau. stability_bad_modifier in
-- common/modifiers/00_static_modifiers.txt applies below 50% stability, scaled
-- by how far below 50% the country sits: scale = (0.5 - stability) / 0.5.
-- Its base values are -50% factory output, -50% dockyard output and
-- -20% political power gain, reached at 0% stability.
--
-- With this change the scale keeps climbing past 0%:
--     stability   0%  -> scale 1.0  ->  -50% factories,  -20% political power
--     stability -50%  -> scale 2.0  -> -100% factories,  -40% political power
--     stability -100% -> scale 3.0  -> -150% factories,  -60% political power
--
-- Occupation is hit as well: RESISTANCE_TARGET_MODIFIER_PER_STABILITY_LOSS is
-- 0.2 per point of stability below 100%, so -100% stability adds roughly
-- +40% resistance target in occupied territory instead of the usual +20% max.
NDefines.NCountry.MIN_STABILITY = -1.0

-- Factory and dockyard output.
-- These are the POWERED values, which is what the game shows you now that the
-- energy system is in: 4.5 per military factory, 2.5 per dockyard.
-- The unpowered counterparts (BASE_FACTORY_SPEED_MIL = 3.5,
-- BASE_FACTORY_SPEED_NAV = 2.0) are deliberately left alone - raise them too if
-- unpowered industry should keep pace.
NDefines.NProduction.POWERED_FACTORY_SPEED_MIL = 7
NDefines.NProduction.POWERED_FACTORY_SPEED_NAV = 4


--------------------------------------------------------------------------
-- AI supply, logistics and hubs.
--
-- Ported from Sheep's Mod (Workshop 3265939166), read line by line against
-- 1.19.2 rather than copied. Vanilla value is recorded beside every line so
-- any single one can be reverted without going back to the source.
--
-- These are the values the AI reads when deciding where to stand, how many
-- divisions a front can hold and what to build behind it. Nothing here
-- changes the supply system itself - the player's logistics are untouched.
-- The system-level half of Sheep's supply work is at the bottom of this
-- file, commented out, because it does change the game for both sides.
--
-- No key here is set by UTTNH_defines.lua or by any other active mod, so
-- nothing is being fought over: defines files all execute in load order and
-- the last assignment wins.
--------------------------------------------------------------------------

-- How many divisions the AI will stack on a front per point of supply.
-- Below 1.0 it plans for fewer men than the hubs can strictly feed, which is
-- the single change that stops it piling forty divisions into a province
-- that supplies eight.
NDefines.NSupply.AI_FRONT_DIVISIONS_PER_SUPPLY_POINT = 0.85   -- vanilla 1.0

-- Safety margin the AI applies to its own supply-use estimate when planning.
-- Higher means it assumes operations will cost more supply than the average
-- suggests, so it commits with headroom instead of exactly to the limit.
NDefines.NAI.AVERAGE_SUPPLY_USE_PESSIMISM = 2.0               -- vanilla 1.5

-- Vanilla assumes at least one unit per province when working out what a
-- front costs to supply, which flatters thinly held sectors. At 0 the
-- estimate follows actual deployment.
NDefines.NSupply.AI_FRONT_MINIMUM_UNITS_PER_PROVINCE_FOR_SUPPLY_CALCULATIONS = 0  -- vanilla 1

-- Reduces the AI's estimate of its own supply headroom, so it errs toward
-- having spare capacity rather than assuming it can grow into the ceiling.
NDefines.NAI.MAX_SUPPLY_DIVISOR = 1.50                        -- vanilla 1.75

-- Weight the AI puts on holding a supply hub when choosing what to defend.
-- More than doubled: hubs become objectives in their own right rather than
-- incidental terrain it happens to be standing on.
NDefines.NAI.LAND_DEFENSE_SUPPLY_HUB_IMPORTANCE = 9           -- vanilla 4

-- How starved a theatre must be before the AI treats it as a supply crisis
-- and reacts. Raising it means it responds at 25% shortfall instead of
-- waiting for 10%.
NDefines.NAITheatre.AI_THEATRE_SUPPLY_CRISIS_LIMIT = 0.25     -- vanilla 0.1

-- Minimum invasion area before the AI will bring floating harbours. Vanilla
-- effectively never does; at 3 it supports small landings, which is what
-- makes an AI amphibious operation survive past the first week.
NDefines.NAI.MIN_INVASION_AREA_SIZE_FOR_FLOATING_HARBORS = 3  -- vanilla 15

-- Construction priorities: the AI has to be willing to BUILD the network the
-- values above assume, or it just becomes cautious rather than capable.
-- Railways are the big one at five times stock priority.
NDefines.NAI.CONSTRUCTION_PRIO_RAILWAY = 20.0                 -- vanilla 4.00
NDefines.NAI.CONSTRUCTION_PRIO_SUPPLY_BUILDING = 3.50         -- vanilla 1.10
NDefines.NAI.CONSTRUCTION_PRIO_FACTOR_OWNED_CORE = 5.0        -- vanilla 2.00
NDefines.NAI.CONSTRUCTION_PRIO_FACTOR_OWNED_NONCORE = 3.0     -- vanilla 1.50

-- WIF ADDITION - not from Sheep's Mod. Read the reasoning before changing it.
--
-- The construction queue is shared, and the two lines above put railways at
-- 20.0 against a civilian factory's vanilla 0.80. That is twenty-five to one.
-- Even unmodified vanilla already favours railways five to one; Sheep's value
-- turns a preference into near-exclusion, and the AI front-loads years of
-- infrastructure before it lays down industry.
--
-- That matters more in this mod than most, for two reasons:
--
--   1. wif_factory_balance.txt works by shifting the military-to-civilian
--      RATIO. It decides the split, not the volume - so if factories barely
--      get queued at all, the cap mechanism has nothing to steer. A capped
--      country escapes only by building civilian factories, and it cannot do
--      that from behind a wall of railways.
--   2. POWERED_FACTORY_SPEED_MIL/NAV at the top of this file make each
--      factory worth roughly double its vanilla output, so a factory
--      deferred costs this mod more than it costs vanilla.
--
-- Both factory priorities are raised by exactly 3x, which leaves the military
-- to civilian ratio at 0.70:0.80 untouched - the cap logic sees precisely the
-- balance it saw before. Railways still lead comfortably at roughly eight to
-- one rather than twenty-five to one, so the supply work above is preserved.
--
-- To undo: delete these two lines. Nothing else depends on them.
NDefines.NAI.CONSTRUCTION_PRIO_CIV_FACTORY = 2.40             -- vanilla 0.80
NDefines.NAI.CONSTRUCTION_PRIO_MIL_FACTORY = 2.10             -- vanilla 0.70


--------------------------------------------------------------------------
-- Fuel, from the same group. Kept separate because it is about training
-- consumption rather than front-line supply, and because the buffer change
-- is aggressive: the AI holds two days of fuel in reserve instead of sixty
-- while burning three times as much on air training. In a mod where fuel is
-- meant to bite, delete these four lines first.
--------------------------------------------------------------------------
NDefines.NAI.MAX_FUEL_CONSUMPTION_RATIO_FOR_NAVY_TRAINING = 0.60   -- vanilla 0.20
NDefines.NAI.MAX_FUEL_CONSUMPTION_RATIO_FOR_AIR_TRAINING = 3.00    -- vanilla 1.0
NDefines.NAI.WANTED_MAX_FUEL_BUFFER_IN_DAYS_FOR_AIR_MAX_CONSUMPTION = 2  -- vanilla 60


--------------------------------------------------------------------------
-- The supply SYSTEM itself - Sheep changes these too, and they apply to the
-- player exactly as much as to the AI. They are a logistics rebalance, not
-- an AI improvement, so they are left off. Uncomment as a block if you want
-- HoI4's supply to be more forgiving for everyone; do not take half of it,
-- since the floating-harbour and railway values are tuned against each other.
--------------------------------------------------------------------------
-- NDefines.NSupply.RAILWAY_BASE_FLOW = 15.0                       -- vanilla 10.0
-- NDefines.NSupply.NODE_INITIAL_SUPPLY_FLOW = 3.05                -- vanilla 2.8
-- NDefines.NSupply.NODE_FLOW_BONUS_PER_RAIL_LEVEL = 0.35          -- vanilla 0.34
-- NDefines.NSupply.SUPPLY_POINTS_PER_TRAIN = 1.25                 -- vanilla 1.0
-- NDefines.NSupply.SUPPLY_FLOW_DROP_REDUCTION_AT_MAX_INFRA = 0.36 -- vanilla 0.30
-- NDefines.NSupply.SUPPLY_FLOW_PENALTY_CROSSING_RIVERS = 0.40     -- vanilla 0.20
-- NDefines.NSupply.RIVER_RAILWAY_LEVEL = 2                        -- vanilla 1
-- NDefines.NSupply.MIN_DIFF_FOR_AUTO_UPDATING_EXISTING_RAILWAYS = 1 -- vanilla 5
-- NDefines.NSupply.VP_TO_SUPPLY_BONUS_CONVERSION = 0.1            -- vanilla 0.05
-- NDefines.NSupply.SUPPLY_HUB_FULL_MOTORIZATION_BONUS = 2.8       -- vanilla 2.2
-- NDefines.NSupply.SUPPLY_HUB_MOTORIZATION_MARGINAL_EFFECT_DECAY = 1.2 -- vanilla 1.6
-- NDefines.NSupply.NAVAL_BASE_INITIAL_SUPPLY_FLOW = 3.60          -- vanilla 3.3
-- NDefines.NSupply.NAVAL_BASE_STARTING_PENALTY_PER_PROVINCE = 0.85 -- vanilla 0.84
-- NDefines.NSupply.FLOATING_HARBOR_BASE_SUPPLY = 50.0             -- vanilla 15.0
-- NDefines.NSupply.FLOATING_HARBOR_INITIAL_SUPPLY_FLOW = 6.0      -- vanilla 2.6
-- NDefines.NSupply.FLOATING_HARBOR_ADDED_PENALTY_PER_PROVINCE = 1.8 -- vanilla 0.8
-- NDefines.NSupply.FLOATING_HARBOR_BASE_DURATION = 60             -- vanilla 21


--------------------------------------------------------------------------
-- AI battle planning.
--
-- Same source and same method as the supply block above. This is the group
-- that decides when the AI attacks, how deep it plans, what it defends and
-- whether it gives ground - the densest AI-only section in Sheep's file.
--
-- Three values are held back at the bottom of this block. Read them before
-- deciding: one of them bears directly on the Moskowien civil war.
--------------------------------------------------------------------------

-- When a unit will join an attack under a plan, by plan priority.
-- Read the two halves together: organisation requirements come DOWN while
-- strength requirements go UP. The AI commits fuller divisions that are less
-- rested, rather than well-rested divisions that have taken losses.
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_LOW = 0.75            -- vanilla 0.85
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_MED = 0.65            -- vanilla 0.7
NDefines.NAI.PLAN_ATTACK_MIN_ORG_FACTOR_HIGH = 0.5            -- vanilla 0.45
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_LOW = 0.75       -- vanilla 0.60
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_MED = 0.65       -- vanilla 0.50
NDefines.NAI.PLAN_ATTACK_MIN_STRENGTH_FACTOR_HIGH = 0.5       -- vanilla 0.30

-- How much expected value a plan needs before the AI actually runs it.
-- More negative means a lower bar. Vanilla drafts plans and sits on them.
NDefines.NAI.PLAN_VALUE_TO_EXECUTE = -0.61                    -- vanilla -0.5

-- How deep the planner searches before abandoning a route.
NDefines.NAI.PLAN_STEP_COST_LIMIT = 15                        -- vanilla 9

-- It no longer gives ground when losing, and values dug-in positions twice
-- as highly. These two belong together: the fallback change alone would just
-- get divisions encircled. Sheep ships both, and so do we.
NDefines.NAI.FALLBACK_LOSING_FACTOR = 0.0                     -- vanilla 1.0
NDefines.NAI.ENTRENCHMENT_WEIGHT = 4.0                        -- vanilla 2.0

-- Only large countries draw fallback lines now; everyone else garrisons.
NDefines.NAI.PLAN_MIN_SIZE_FOR_FALLBACK = 2000                -- vanilla 50

-- Armour is kept out of terrain that wastes it.
NDefines.NAI.ASSIGN_TANKS_TO_MOUNTAINS = -15                  -- vanilla -6.0
NDefines.NAI.ASSIGN_TANKS_TO_JUNGLE = -20                     -- vanilla -6.0

-- Encirclements: stop chasing enormous speculative pockets, and only attempt
-- ones that can actually be closed. The distance cut is the big one.
NDefines.NAI.POCKET_DISTANCE_MAX = 6000                       -- vanilla 40000
NDefines.NAI.MICRO_POCKET_SIZE = 3                            -- vanilla 4
NDefines.NAI.MAX_MICRO_ATTACKS_PER_ORDER = 5                  -- vanilla 3
NDefines.NAI.MIN_PLAN_VALUE_TO_MICRO_INACTIVE = 0.15          -- vanilla 0.25

-- Front shape: what counts as a bulge worth acting on, how close to the edge
-- a cut has to be, and how accurately it reads the units opposite.
NDefines.NAI.FRONT_BULGE_RATIO_LOWER_CUTOFF = 1.2             -- vanilla 0.95
NDefines.NAI.FRONT_BULGE_RATIO_UPPER_CUTOFF = 1.8             -- vanilla 1.5
NDefines.NAI.FRONT_CUTOFF_MIN_EDGE_PROXIMITY = 1              -- vanilla 2
NDefines.NAI.FRONT_EVAL_UNIT_ACCURACY = 1.5                   -- vanilla 1.0

-- More of the army committed to active fronts, and more of it allowed to
-- mass on one front before that front counts as saturated.
NDefines.NAI.RESERVE_TO_COMMITTED_BALANCE = 0.15              -- vanilla 0.3
NDefines.NAI.FRONT_UNITS_CAP_FACTOR = 20.0                    -- vanilla 15.0

-- Target selection. Mid-value victory points stop dominating, so it goes for
-- militarily useful ground rather than chasing dots on the map. It also
-- reacts twice as hard to emerging threats, and spreads attention slightly
-- more evenly instead of fixating on the single main enemy.
NDefines.NAI.VP_LEVEL_IMPORTANCE_MEDIUM = 1                   -- vanilla 10
NDefines.NAI.DYNAMIC_STRATEGIES_THREAT_FACTOR = 8.0           -- vanilla 4.0
NDefines.NAI.MAIN_ENEMY_FRONT_IMPORTANCE = 3.0                -- vanilla 4.0

-- How much of a state it needs to hold before assigning area defence to it.
NDefines.NAI.STATE_CONTROL_FOR_AREA_DEFENSE = 0.60            -- vanilla 0.4

-- Raids are attempted far less often, freeing command power for planning.
NDefines.NAI.RAIDS_CREATE_FREQUENCY_DAYS = 20                 -- vanilla 7


--------------------------------------------------------------------------
-- Held back from the battle planning group. Each for a different reason.
--------------------------------------------------------------------------

-- 1. AREA_DEFENSE_CIVIL_WAR_IMPORTANCE. Left OFF deliberately.
--
-- This controls how heavily the AI weights area defence for a country that is
-- in a civil war, "as target or revolter" in Paradox's own wording. Sheep cuts
-- it to a sixth, which suits vanilla where civil wars are a sideshow.
--
-- Welt in Flammen is built around one. wif_nsr_revolt creates NSR, NSP, NAR,
-- NWG, LOK, RLF, WRS, SRG, NRG and SSM in a single effect, all of them at war
-- with Moskowien and most of them with each other. Enabling this tells every
-- one of those AIs to care far less about defending its own territory, in the
-- exact scenario the mod exists to stage. Sheep also marks this line "test"
-- in their own file, so it is not settled on their side either.
--
-- Try it only if the breakaways feel too passive, and expect the civil war to
-- become considerably more fluid.
-- NDefines.NAI.AREA_DEFENSE_CIVIL_WAR_IMPORTANCE = 5.0        -- vanilla 30

-- 2. PLAN_ACTIVATION_PLAYER_WEIGHT_FACTOR. Left OFF deliberately.
--
-- How much extra weight the AI gives to fronts facing a human. Sheep cuts it
-- 25-fold, which stops the whole world dogpiling the player - a reasonable
-- multiplayer-ish choice, but it makes the AI press you far less hard. That
-- is the opposite of why you are porting this mod.
-- NDefines.NAI.PLAN_ACTIVATION_PLAYER_WEIGHT_FACTOR = 2       -- vanilla 50.0

-- 3. The three global ones. These change how battle plans work for YOUR
-- orders as much as the AI's - pocket automation, how far a frontline order
-- stretches, and how short a path has to be before units redeploy along it.
-- Uncomment only if you want your own plan drawing to behave differently too.
-- NDefines.NMilitary.PLAN_MIN_AUTOMATED_EMPTY_POCKET_SIZE = 15 -- vanilla 2
-- NDefines.NMilitary.FRONTLINE_EXPANSION_FACTOR = 0.7          -- vanilla 0.6
-- NDefines.NMilitary.FRONT_MIN_PATH_TO_REDEPLOY = 4            -- vanilla 8


--------------------------------------------------------------------------
-- AI division design and fielding.
--
-- What the AI puts in the field, when it lets a division leave the training
-- queue, and which templates it sends where. The construction values that
-- pair with this group are already up in the supply block.
--------------------------------------------------------------------------

-- When a division is allowed out of the training queue. Training goes UP to
-- 100% while the equipment bar comes DOWN hard - the AI now fields divisions
-- that are fully trained and short of kit, rather than fully equipped and
-- half trained.
--
-- This matters more here than in vanilla. wif_military_factory_ceiling caps
-- how much arms industry a country can run, so equipment is genuinely scarce
-- in this mod. At vanilla's 98% the AI sits on finished divisions waiting for
-- rifles that are never coming; at 70% it puts them on the line.
NDefines.NAI.DEPLOY_MIN_TRAINING_PEACE_FACTOR = 1              -- vanilla 0.98
NDefines.NAI.DEPLOY_MIN_TRAINING_WAR_FACTOR = 1                -- vanilla 0.95
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_PEACE_FACTOR = 0.70          -- vanilla 0.98
NDefines.NAI.DEPLOY_MIN_EQUIPMENT_WAR_FACTOR = 0.85            -- vanilla 0.95

-- And it keeps them in training marginally longer before calling them done.
NDefines.NAI.STOP_TRAINING_FULLY_TRAINED_FACTOR = 0.99         -- vanilla 0.95

-- The garrison split, and the sharpest single idea in Sheep's file.
-- Cheap low-priority templates get an enormous bonus for garrison duty and an
-- outright NEGATIVE score for front-line duty. Together these stop the AI
-- garrisoning occupied territory with the same divisions it needs at the
-- front - which is exactly what Moskowien spends the civil war doing.
NDefines.NAI.LOW_PRIO_TEMPLATE_BONUS_FOR_GARRISONS = 300000    -- vanilla 1000
NDefines.NAI.LOW_PRIO_TEMPLATE_PENALTY_FOR_FRONTS = -2000      -- vanilla 500

-- Modernisation: far less reluctant to upgrade existing divisions, but doing
-- it in smaller batches so fewer are off the line at any one time.
NDefines.NAI.UPGRADE_DIVISION_RELUCTANCE = 3                   -- vanilla 7
NDefines.NAI.UPGRADE_PERCENTAGE_OF_FORCES = 0.10               -- vanilla 0.20

-- Twelve times more willing to spend army XP improving its templates.
-- Vanilla AI hoards experience it then never uses.
NDefines.NAI.DESIRE_USE_XP_TO_UPDATE_LAND_TEMPLATE = 25.0      -- vanilla 2.0

-- It only motorises divisions when supply genuinely supports the extra draw.
NDefines.NAI.DIVISION_SUPPLY_RATIO_TO_MOTORIZE = 1             -- vanilla 0.80


-- Held back: the three global division-designer costs. These cut what the
-- designer charges in army XP for EVERYONE, by a factor of 5 to 20. That is
-- a balance decision about your own template building, not an AI change.
-- NDefines.NMilitary.BASE_DIVISION_BRIGADE_GROUP_COST = 1     -- vanilla 20
-- NDefines.NMilitary.BASE_DIVISION_BRIGADE_CHANGE_COST = 1    -- vanilla 5
-- NDefines.NMilitary.BASE_DIVISION_SUPPORT_SLOT_COST = 1      -- vanilla 10


--------------------------------------------------------------------------
-- AI production and industry.
--
-- The smallest useful group so far: of Sheep's twenty production values only
-- nine are AI logic, and the eleven global ones need more thought here than
-- in any previous block. See the note at the bottom before enabling them.
--------------------------------------------------------------------------

-- Railway guns. Vanilla AI builds them far too eagerly and ties up factories
-- it needs for equipment. All three thresholds are raised hard: five times as
-- many divisions and five times as many factories required before it will
-- start, plus a ratio floor it did not have at all before.
NDefines.NAI.RAILWAY_GUN_PRODUCTION_MIN_DIVISONS = 100         -- vanilla 20
NDefines.NAI.RAILWAY_GUN_PRODUCTION_MIN_FACTORIES = 50         -- vanilla 10
NDefines.NAI.RAILWAY_GUN_PRODUCTION_BASE_DIVISIONS_RATIO_PERCENT = 5  -- vanilla 0

-- Production line stability. It tolerates less standing surplus before
-- moving a line onto something else, but then requires a bigger surplus to
-- justify the switch - so it reacts to genuine oversupply without flapping
-- between designs and losing efficiency each time.
NDefines.NAI.PRODUCTION_EQUIPMENT_SURPLUS_FACTOR = 0.6         -- vanilla 0.8
NDefines.NAI.PRODUCTION_LINE_SWITCH_SURPLUS_NEEDED_MODIFIER = 0.4  -- vanilla 0.2

-- Military-industrial organisations: pick the best available production
-- assignment rather than rolling among the top three.
NDefines.NAI.INDUSTRIAL_ORG_PRODUCTION_ASSIGN_RANDOMNESS = 1.0 -- vanilla 3

-- Fuel lend-lease. It asks while it still has four months of fuel instead of
-- waiting until two days remain, so requests arrive in time to matter.
NDefines.NAI.MINIMUM_FUEL_DAYS_TO_ASK_LEND_LEASE = 120         -- vanilla 2
NDefines.NAI.MINIMUM_FUEL_DAYS_TO_ACCEPT_LEND_LEASE = 2        -- vanilla 10

-- How much of its civilian industry the AI will commit to imports.
--
-- NOT PORTED. Sheep raises this to 1.0; vanilla's comment is "Will at most
-- trade away this fraction of factories", so 1.0 lets the AI put its entire
-- civilian industry on the market and keep nothing back for construction.
--
-- That collides head-on with the military factory cap in
-- common/ai_strategy/wif_factory_balance.txt. The whole mechanism depends on
-- a capped country building CIVILIAN factories to raise its own ceiling - if
-- its civs are all committed to trade, it cannot build them, and the country
-- sits at the cap permanently with no way out.
--
-- Sheep also sets NTrade.TRADEABLE_FACTORIES_FRACTION = 2.0, one of the
-- twelve keys that no longer exists in 1.19, so this corner was guesswork on
-- their side anyway. Left at vanilla.
-- NDefines.NAI.TRADEABLE_FACTORIES_FRACTION = 1.0             -- vanilla 0.8


--------------------------------------------------------------------------
-- The eleven global production rules. Left OFF, and this block deserves
-- more caution than the earlier ones.
--
-- Welt in Flammen already has a deliberate industrial design: military
-- factories are capped by wif_military_factory_ceiling, and the two POWERED
-- factory speeds at the top of this file roughly double what a factory
-- produces. Fewer factories, each worth more - that tension is the point.
--
-- Sheep's global production values push the other way: free licensing, no
-- efficiency loss when switching variant, lend-lease in half the time. None
-- of it is broken, but together it loosens exactly the constraint this mod
-- was built around, and it does so for the player as much as the AI.
--
-- Enable them only if you decide the industry side should be more forgiving.
--------------------------------------------------------------------------
-- NDefines.NProduction.BASE_LICENSE_IC_COST = 0                         -- vanilla 1
-- NDefines.NProduction.LICENSE_IC_COST_YEAR_INCREASE = 0                -- vanilla 1
-- NDefines.NProduction.LICENSE_EQUIPMENT_SPEED_NOT_FACTION = 0.0        -- vanilla -0.10
-- NDefines.NDiplomacy.LICENSE_ACCEPTANCE_SAME_FACTION = 1000            -- vanilla 20
-- NDefines.NProduction.LEND_LEASE_DELIVERY_TOTAL_DAYS = 14              -- vanilla 30
-- NDefines.NProduction.EQUIPMENT_LEND_LEASE_WEIGHT_FACTOR = 0.0025      -- vanilla 0.01
-- NDefines.NProduction.BASE_FACTORY_EFFICIENCY_VARIANT_CHANGE_FACTOR = 100  -- vanilla 90
-- NDefines.NProduction.RAILWAY_GUN_MAX_MIL_FACTORIES_PER_LINE = 10      -- vanilla 5
-- NDefines.NProduction.RAILWAY_GUN_REPAIR_SPEED = 25.0                  -- vanilla 8.0
-- NDefines.NIndustrialOrganisation.ASSIGN_DESIGN_TEAM_PP_COST_PER_DAY = 0.05  -- vanilla 0.1
-- NDefines.NIndustrialOrganisation.DEFAULT_INITIAL_POLICY_ATTACH_COST = 0     -- vanilla 25


--------------------------------------------------------------------------
-- AI front control (AIFC).
--
-- The frontline controller added in the later patches: how often it wakes,
-- where it routes a front, what it aims at, and how it rates its own
-- divisions. All twenty-three values are AI-only - there is no player-facing
-- half to this group at all, which makes it the cleanest block in the file.
--------------------------------------------------------------------------

-- How it rates one of its own divisions for offensive work. These weights are
-- where the character of the change lives: armour counts nearly three times
-- as much and hardness almost three times, so the controller recognises which
-- divisions are actually good and concentrates them, rather than smearing
-- everything evenly along the line the way vanilla does.
NDefines.NAI.AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_ARMOR = 80.0     -- vanilla 30.0
NDefines.NAI.AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_HARDNESS = 800.0 -- vanilla 300.0
NDefines.NAI.AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_EXPERIENCE = 500.0  -- vanilla 300.0
NDefines.NAI.AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_SOFT_ATTACK = 12.0  -- vanilla 6.0
NDefines.NAI.AIFC_UNIT_OFFENSIVE_SCORE_FACTOR_HARD_ATTACK = 16.0  -- vanilla 8.0

-- What a front aims at. Supply hubs and naval bases both become materially
-- more attractive objectives, and naval bases now scale properly with level.
-- The short-path penalty is removed entirely, so it stops discounting
-- objectives simply for being close.
NDefines.NAI.AIFC_TARGET_SUPPLY_HUB_BASE_SCORE = 30.0          -- vanilla 20.0
NDefines.NAI.AIFC_TARGET_NAVAL_BASE_BASE_SCORE = 15.0          -- vanilla 10.0
NDefines.NAI.AIFC_TARGET_NAVAL_BASE_SCORE_PER_LEVEL = 2.0      -- vanilla 1.0
NDefines.NAI.AIFC_TARGET_SHORT_PATH_PENALTY_FACTOR = 0         -- vanilla 0.1

-- Terrain pathing. Note the inversion: urban gets HALF its vanilla cost while
-- plains nearly double. Fronts now route through built-up ground rather than
-- open country, which is where infantry actually wants to be fighting.
-- Mountains get dearer, ordinary rivers cheaper, major rivers dearer still.
NDefines.NAI.AIFC_PATH_COST_TRN_URBAN = 0.50                   -- vanilla 1.0
NDefines.NAI.AIFC_PATH_COST_TRN_PLAINS = 1.5                   -- vanilla 0.8
NDefines.NAI.AIFC_PATH_COST_TRN_FOREST = 1.5                   -- vanilla 1.2
NDefines.NAI.AIFC_PATH_COST_TRN_MOUNTAINS = 4.0                -- vanilla 3.0
NDefines.NAI.AIFC_PATH_COST_ADJ_RIVER = 1.5                    -- vanilla 2.0
NDefines.NAI.AIFC_PATH_COST_ADJ_RIVER_LARGE = 3.25             -- vanilla 3.0
NDefines.NAI.AIFC_PATH_COST_RAILWAY_CONNECTION = 0.80          -- vanilla 0.75

-- Cadence and density. It re-evaluates fronts a day sooner, nudges units
-- every ten days instead of fifteen, refreshes its needs twice as fast, and
-- holds the line slightly thinner at 2.5 divisions per province.
NDefines.NAI.AIFC_UPDATE_FREQUENCY_DAYS = 4                    -- vanilla 5
NDefines.NAI.AIFC_UNIT_NUDGE_FREQUENCY_DAYS = 10.0             -- vanilla 15
NDefines.NAI.AIFC_REFRESH_NEED_PER_DAY = 2.0                   -- vanilla 1.0
NDefines.NAI.AIFC_REFRESH_NEED_SUPPLY_FACTOR_PER_DAY = 1.10    -- vanilla 0.8
NDefines.NAI.AIFC_FRESHNESS_ADD_ON_PROGRESS = 22.0             -- vanilla 25.0
NDefines.NAI.AIFC_CA_DIVISIONS_PER_PROVINCE = 2.5              -- vanilla 3

-- It waits for twice the average organisation before activating a front.
NDefines.NAI.AIFC_ACTIVATE_AVG_ORG_RATIO_THRESHOLD = 0.4       -- vanilla 0.2


--------------------------------------------------------------------------
-- AI experience spending.
--
-- Vanilla AI hoards army, navy and air XP it then never spends. These are
-- the "desire" weights that decide what it buys, and they compete with each
-- other for one pool - so the ratios matter more than the absolute numbers.
-- With land equipment at 50 and templates at 25 (already set in the division
-- block above), equipment upgrades outrank template work, which outranks
-- doctrine at 10.
--
-- Worth knowing: Sheep tuned these alongside global cuts to what XP COSTS,
-- which are held back below. Without those, the AI still spends in this
-- priority order but has less to spend, so expect the effect to be real but
-- less dramatic than in their build.
--------------------------------------------------------------------------
NDefines.NAI.DESIRE_USE_XP_TO_UPGRADE_LAND_EQUIPMENT = 50.0    -- vanilla 1.0
NDefines.NAI.DESIRE_USE_XP_TO_UPGRADE_AIR_EQUIPMENT = 15.0     -- vanilla 1.0
NDefines.NAI.DESIRE_USE_XP_TO_UNLOCK_LAND_DOCTRINE = 10        -- vanilla 0.5
NDefines.NAI.DESIRE_USE_XP_TO_UNLOCK_ARMY_SPIRIT = 0.4         -- vanilla 0.35

-- How much XP it holds in reserve before designing a variant, and how much
-- it insists on having banked before creating one at all. Lower across the
-- board: it designs earlier instead of saving for a rainy day.
NDefines.NAI.VARIANT_CREATION_XP_RESERVE_LAND = 10             -- vanilla 50
NDefines.NAI.VARIANT_CREATION_XP_RESERVE_NAVY = 30             -- vanilla 50
NDefines.NAI.VARIANT_CREATION_XP_RESERVE_AIR = 30              -- vanilla 50
NDefines.NAI.DEFAULT_LEGACY_VARIANT_CREATION_XP_CUTOFF_LAND = 20  -- vanilla 35
NDefines.NAI.DEFAULT_MODULE_VARIANT_CREATION_XP_CUTOFF_LAND = 10  -- vanilla 35
NDefines.NAI.DEFAULT_LEGACY_VARIANT_CREATION_XP_CUTOFF_AIR = 20   -- vanilla 25


--------------------------------------------------------------------------
-- The fourteen global XP rules. Left OFF.
--
-- These change what experience COSTS and what it can accumulate to, for you
-- exactly as much as the AI: land equipment design drops from 10 to 3, naval
-- and air from 25 to 1, every ramp cost to zero, module work to 1, and the
-- XP ceiling from 500 to 999. UNIT_EXP_LEVELS also moves the green/regular/
-- veteran/elite thresholds for every division in the game.
--
-- That is a substantial rebalance of the whole experience economy. Enable as
-- a block if you want it - the AI desire values above are tuned expecting it.
--------------------------------------------------------------------------
-- NDefines.NMilitary.LAND_EQUIPMENT_BASE_COST = 3                -- vanilla 10
-- NDefines.NMilitary.LAND_EQUIPMENT_RAMP_COST = 0                -- vanilla 5
-- NDefines.NMilitary.NAVAL_EQUIPMENT_BASE_COST = 1               -- vanilla 25
-- NDefines.NMilitary.NAVAL_EQUIPMENT_RAMP_COST = 0               -- vanilla 5
-- NDefines.NMilitary.AIR_EQUIPMENT_BASE_COST = 1                 -- vanilla 25
-- NDefines.NMilitary.AIR_EQUIPMENT_RAMP_COST = 0                 -- vanilla 5
-- NDefines.NMilitary.MAX_ARMY_EXPERIENCE = 999                   -- vanilla 500
-- NDefines.NMilitary.MAX_NAVY_EXPERIENCE = 999                   -- vanilla 500
-- NDefines.NMilitary.MAX_AIR_EXPERIENCE = 999                    -- vanilla 500
-- NDefines.NProduction.EQUIPMENT_MODULE_ADD_XP_COST = 1          -- vanilla 5.0
-- NDefines.NProduction.EQUIPMENT_MODULE_REPLACE_XP_COST = 1      -- vanilla 6.0
-- NDefines.NProduction.EQUIPMENT_MODULE_CONVERT_XP_COST = 1      -- vanilla 3.0
-- NDefines.NProduction.LICENSE_EQUIPMENT_UPGRADE_XP_FACTOR = 1   -- vanilla 2.0
-- NDefines.NMilitary.UNIT_EXP_LEVELS = { 0.10, 0.20, 0.80, 0.95 }  -- vanilla { 0.1, 0.3, 0.75, 0.9 }


--------------------------------------------------------------------------
-- AI generals and command power.
--
-- Small group, and the one where reading Paradox's own comments changed the
-- conclusion. Two of these do not do what their names suggest - both are
-- explained where they sit.
--------------------------------------------------------------------------

-- How much a general's trait COUNT weighs when the AI decides which general
-- to give an army to.
--
-- The name reads like a switch for handing out traits. It is not. Vanilla's
-- own comment is "This times general's nr of active traits is added to
-- score", so it is purely a term in the leader-selection score. At 0 the AI
-- stops favouring a general simply for having collected more traits, and
-- picks on the rest of the criteria instead. Sensible, given it also starts
-- buying traits earlier on the line below.
NDefines.NAI.ARMY_LEADER_ASSIGN_NR_TRAITS = 0                  -- vanilla 5

-- Command power the AI banks before it will spend any on traits. Undocumented
-- in vanilla, but the direction is clear: it starts buying much earlier.
NDefines.NAI.COMMAND_POWER_BEFORE_SPEND_ON_TRAITS = 10.0       -- vanilla 30.0

-- Chance for the AI to pick a preferred tactic when it has none.
--
-- At 0 it never picks one at all - not "picks less often". A preferred tactic
-- locks a country into trying that tactic every combat round, so declining to
-- set one leaves the normal adaptive selection running. That appears to be
-- the intent, and it is why the global cost change for tactics is held back
-- below: if the AI never buys one, making them free only benefits you.
NDefines.NAI.AI_PREFERRED_TACTIC_WEEKLY_CHANGE_CHANCE = 0.00   -- vanilla 0.05

-- Minimum command power CAP before the AI will create raids.
--
-- Read this one carefully. BASE_MAX_COMMAND_POWER is 80.0, so a threshold of
-- 150 is not reachable without large modifiers - in practice this stops most
-- countries raiding entirely rather than merely rarely. AI raids are widely
-- reckoned a waste of command power, so that is probably deliberate on
-- Sheep's part, but it is closer to switching the feature off than tuning it.
-- Revert to 60 if you want AI raids back.
NDefines.NAI.RAIDS_COMMAND_POWER_CAP_TO_CREATE = 150.0         -- vanilla 60.0

-- Military-industrial trait unlocks: take the best rather than rolling among
-- the top three. Matches the production-assignment value already set above.
NDefines.NAI.INDUSTRIAL_ORG_TRAIT_UNLOCK_RANDOMNESS = 1.0      -- vanilla 3


-- Held back: the four global ones. Every one of these applies to your own
-- generals as much as the AI's - free tactic switching, cheaper traits,
-- leaders regaining their modifiers in a day instead of a fortnight after
-- being moved, and more experience from attaches. The cooldown one in
-- particular is a significant quality-of-life change to army reorganisation.
-- NDefines.NMilitary.PREFERRED_TACTIC_COMMAND_POWER_COST = 0        -- vanilla 20
-- NDefines.NMilitary.UNIT_LEADER_ASSIGN_TRAIT_COST = 10.0           -- vanilla 15.0
-- NDefines.NMilitary.UNIT_LEADER_MODIFIER_COOLDOWN_ON_GROUP_CHANGE = 1  -- vanilla 15
-- NDefines.NCountry.ATTACHE_XP_SHARE = 0.20                         -- vanilla 0.15


--------------------------------------------------------------------------
-- AI navy.
--
-- Fleet composition, task force shapes, and what the AI does with the ships
-- it has. Note that Sheep assigns SCREEN_TASKFORCE_MAX_SHIP_COUNT twice in
-- their file - 5 in one place and 24 in another. The later assignment wins in
-- Lua, so 24 is what their mod actually runs; only that value is taken here.
--------------------------------------------------------------------------

-- Fleet shape. Task forces get much larger overall, but the composition
-- changes: more screens per capital, more capitals per carrier, and
-- submarine groups cut to a third so they hunt in small packs.
NDefines.NAI.NAVY_PREFERED_MAX_SIZE = 80                       -- vanilla 25
NDefines.NAI.CAPITAL_TASKFORCE_MAX_CAPITAL_COUNT = 16          -- vanilla 12
NDefines.NAI.CARRIER_TASKFORCE_MAX_CARRIER_COUNT = 8           -- vanilla 4
NDefines.NAI.SCREEN_TASKFORCE_MAX_SHIP_COUNT = 24              -- vanilla 12
NDefines.NAI.SCREENS_TO_CAPITAL_RATIO = 5.0                    -- vanilla 4.0

-- Submarine task force size is deliberately NOT ported.
--
-- Sheep sets it twice: 6 on line 270 of their file, then 16 on line 289. Lua
-- takes the last assignment, and 16 is vanilla - so despite appearances their
-- mod does not change this value at all. Porting the 6 would mean shipping
-- something their build has never actually run.
--
-- The 6 was plainly the intent though, and small submarine packs are a
-- defensible choice. Enable it if you want that, knowing it is your decision
-- rather than theirs.
-- NDefines.NAI.SUB_TASKFORCE_MAX_SHIP_COUNT = 6               -- vanilla 16
NDefines.NAI.CAPITALS_TO_CARRIER_RATIO = 2                     -- vanilla 1.5
NDefines.NAI.MIN_CAPITALS_FOR_CARRIER_TASKFORCE = 8            -- vanilla 6

-- Refits are effectively switched off. Vanilla AI ties up dockyards refitting
-- ships forever; at 5000 reluctance it simply stops, and when it does refit it
-- does a third of the fleet at once rather than a tenth.
NDefines.NAI.REFIT_SHIP_RELUCTANCE = 5000                      -- vanilla 28
NDefines.NAI.REFIT_SHIP_PERCENTAGE_OF_FORCES = 0.33            -- vanilla 0.1

-- How keen a country is to build dockyards at all, scaled by how naval it is.
-- More negative means land powers stop sinking industry into a navy they will
-- never use - which is most of the countries in this mod.
NDefines.NAI.DOCKYARDS_PER_NAVAL_DESIRE_EFFECT = -50.0         -- vanilla -20.0

-- Mine warfare: far fewer screens diverted to sweeping and laying, and the
-- threshold at which sweeping becomes top priority drops hard, so it reacts
-- to real minefields instead of committing ships pre-emptively.
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING = 0.05    -- vanilla 0.10
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_MINE_LAYING = 0.05      -- vanilla 0.10
NDefines.NAI.MAX_SCREEN_TASKFORCES_FOR_MINE_SWEEPING_PRIO_MAX_MINES = 200  -- vanilla 1000

-- Convoy raiding response. It takes four times as much sunk tonnage before
-- the AI writes a sea region off, but the danger it remembers decays five
-- times faster - so it holds contested water instead of abandoning it, then
-- forgets old losses quickly.
NDefines.NAI.REGION_THREAT_LEVEL_TO_BLOCK_REGION = 25 * 400    -- vanilla 25 * 100
NDefines.NAI.REGION_CONVOY_DANGER_DAILY_DECAY = 10             -- vanilla 2

-- Air support for naval work: far more bombers requested per enemy ship, and
-- twice the patrol aircraft per escorting ship.
NDefines.NAI.NAVAL_STRIKE_PLANES_PER_SHIP = 50                 -- vanilla 20
NDefines.NAI.NAVAL_PATROL_PLANES_PER_SHIP_ESCORTING = 20       -- vanilla 10.0

-- A naval invasion keeps its priority far longer before being treated as an
-- ordinary front, so landings get reinforced instead of stalling on the beach.
NDefines.NAI.MIN_NUM_CONQUERED_PROVINCES_TO_DEPRIO_NAVAL_INVADED_FRONTS = 100  -- vanilla 20

-- Sea distance stops penalising trade partner choice.
NDefines.NAI.SEA_PATH_LENGTH_SCORE_BASE = 0                    -- vanilla -30


--------------------------------------------------------------------------
-- AI air.
--
-- Almost entirely about how heavily the AI weights air support when it looks
-- at a land battle. The headline is OUR_COMBATS: air over its own ongoing
-- combats goes up more than sixfold, which is what makes AI aircraft turn up
-- where the fighting actually is instead of drifting.
--------------------------------------------------------------------------
NDefines.NAI.LAND_COMBAT_OUR_COMBATS_AIR_IMPORTANCE = 1000     -- vanilla 155
NDefines.NAI.LAND_COMBAT_ENEMY_COASTAL_FORTS_AIR_IMPORTANCE = 20.0  -- vanilla 3
NDefines.NAI.LAND_COMBAT_FRIEND_COMBATS_AIR_IMPORTANCE = 5.0   -- vanilla 8
NDefines.NAI.LAND_COMBAT_OUR_ARMIES_AIR_IMPORTANCE = 8.0       -- vanilla 20
NDefines.NAI.LAND_COMBAT_FRIEND_ARMIES_AIR_IMPORTANCE = 2.0    -- vanilla 10

-- Read those five together: the weight moves off standing armies and onto
-- armies that are actually in combat right now. That is the whole idea.

-- It values air superiority twice as highly when judging a front, and asks
-- for three times the fighters per enemy plane in offensive air, 2.5x on the
-- defensive.
NDefines.NAI.FRONT_EVAL_UNIT_AIR_SUP_IMPACT = 2.0              -- vanilla 1.0
NDefines.NAI.LAND_COMBAT_FIGHTERS_PER_PLANE = 3.0              -- vanilla 1.0
NDefines.NAI.LAND_DEFENSE_FIGHERS_PER_PLANE = 2.5              -- vanilla 1.8

-- Distance stops factoring into where air is sent, it re-prioritises wings
-- weekly rather than every four days, and it will not rebase a wing already
-- covering three quarters of its region.
NDefines.NAI.AIR_SCORE_DISTANCE_IMPACT = 0.0                   -- vanilla 0.3
NDefines.NAI.DAYS_BETWEEN_AIR_PRIORITIES_UPDATE = 7            -- vanilla 4
NDefines.NAI.AI_AIR_MISSION_COVERAGE_TO_STAY_PUT = 0.75        -- vanilla 0.5


-- Held back: the twenty-two global navy rules and one global air rule. These
-- change naval combat itself for both sides - submarine detection doubled,
-- training accidents halved, repair-and-return thresholds, torpedo reveal
-- chance, convoy detection, and NAVAL_INVASION_PLANNING_BONUS_MALUS going
-- from 0 to -0.9, which is a large nerf to invasion planning bonuses for
-- everyone. Left off as a block.
-- NDefines.NNavy.SUB_DETECTION_CHANCE_BASE = 10                  -- vanilla 5
-- NDefines.NNavy.CONVOY_DETECTION_CHANCE_BASE = 2.68             -- vanilla 4.12
-- NDefines.NNavy.SUBMARINE_BASE_TORPEDO_REVEAL_CHANCE = 0.06     -- vanilla 0.035
-- NDefines.NNavy.TRAINING_ACCIDENT_CHANCES = 0.01                -- vanilla 0.02
-- NDefines.NNavy.TRAINING_ACCIDENT_CRITICAL_HIT_CHANCES = 0.15   -- vanilla 0.3
-- NDefines.NNavy.TRAINING_ACCIDENT_STRENGTH_LOSS = 2.0           -- vanilla 4.0
-- NDefines.NNavy.TRAINING_ORG = 0.40                             -- vanilla 0.2
-- NDefines.NNavy.HOLD_MISSION_MOVEMENT_COST = 0.8                -- vanilla 1.0
-- NDefines.NNavy.REPAIR_AND_RETURN_AMOUNT_SHIPS_LOW = 0.1        -- vanilla 0.2
-- NDefines.NNavy.REPAIR_AND_RETURN_AMOUNT_SHIPS_HIGH = 0.3       -- vanilla 0.2
-- NDefines.NNavy.REPAIR_AND_RETURN_UNIT_DYING_STR = 0.15         -- vanilla 0.2
-- NDefines.NNavy.REPAIR_AND_RETURN_PRIO_MEDIUM_COMBAT = 0.2      -- vanilla 0.6
-- NDefines.NNavy.REPAIR_AND_RETURN_PRIO_LOW_COMBAT = 0.3         -- vanilla 0.9
-- NDefines.NNavy.BEST_CAPITALS_TO_SCREENS_RATIO = 0.20           -- vanilla 0.25
-- NDefines.NNavy.BEST_CAPITALS_TO_CARRIER_RATIO = 2              -- vanilla 1
-- NDefines.NNavy.MAX_CAPITALS_PER_AUTO_TASK_FORCE = 30           -- vanilla 5
-- NDefines.NNavy.SHORE_BOMBARDMENT_CAP = 0.35                    -- vanilla 0.33
-- NDefines.NNavy.UNIT_TRANSFER_SPOTTING_SPEED_MULT = 3.0         -- vanilla 5.0
-- NDefines.NNavy.AMPHIBIOUS_INVADE_DEFEND_LOW = 1.1              -- vanilla 1.5
-- NDefines.NMilitary.NAVAL_INVASION_PLANNING_BONUS_MALUS = -0.9  -- vanilla 0
-- NDefines.NCountry.NAVY_USE_HOME_BASE_FOR_RANGE = false         -- vanilla true
-- NDefines.NAir.AIR_WING_FLIGHT_SPEED_MULT = 0.05                -- vanilla 0.02


--------------------------------------------------------------------------
-- AI research.
--
-- These matter more in this mod than they look, because UTTNH continues the
-- tech tree to 1990 - see common/ai_strategy/wif_uttnh_research.txt. Two of
-- them directly govern whether the AI will climb past the year it is in.
--------------------------------------------------------------------------

-- It re-weighs research every day instead of every seven, so it reacts to the
-- war it is actually fighting rather than the one it was in last week.
NDefines.NAI.RESEARCH_DAYS_BETWEEN_WEIGHT_UPDATE = 1            -- vanilla 7

-- How far ahead of its year the AI will consider researching, and how much it
-- minds the penalty for doing so. Vanilla will not look more than three years
-- up the tree; at 7, and caring far less about the penalty, it keeps climbing
-- instead of stalling at the edge of its era. With UTTNH's post-war folders
-- this is the difference between an AI that reaches jets and main battle
-- tanks on schedule and one that sits on 1945 equipment into the sixties.
NDefines.NAI.MAX_AHEAD_RESEARCH_PENALTY = 7                     -- vanilla 3
NDefines.NAI.RESEARCH_AHEAD_OF_TIME_FACTOR = 1.5                -- vanilla 4.0

-- Counter-intuitive but deliberate: vanilla AI over-values rushing technology
-- for the ahead-of-time bonus and eats the malus doing it. Caring less about
-- both bonus and speed makes it research on schedule.
NDefines.NAI.RESEARCH_AHEAD_BONUS_FACTOR = 10.0                 -- vanilla 25.0
NDefines.NAI.RESEARCH_BONUS_FACTOR = 2                          -- vanilla 5.0

-- Assign the best military-industrial organisation to a research slot rather
-- than rolling among the top three.
NDefines.NAI.INDUSTRIAL_ORG_RESEARCH_ASSIGN_RANDOMNESS = 1.0    -- vanilla 3


--------------------------------------------------------------------------
-- AI diplomacy, trade, combat and peace. The last of the AI-only values.
--------------------------------------------------------------------------

-- Volunteers. Vanilla caps a country at sending a quarter of its army; at
-- 1.00 minors can commit properly, and the receiving AI is three times more
-- willing to take them. In a mod where a dozen breakaways fight at once, this
-- is what lets them actually help each other.
NDefines.NAI.MAX_VOLUNTEER_ARMY_FRACTION = 1.00                 -- vanilla 0.25
NDefines.NAI.DIPLOMACY_ACCEPT_VOLUNTEERS_BASE = 150             -- vanilla 50

-- It stops handing its army away as expeditionary forces entirely, and holds
-- out harder for the faction it actually wants to join.
NDefines.NAI.DIPLOMACY_SEND_MAX_FACTION = 0.0                   -- vanilla 0.75
NDefines.NAI.DIPLO_PREFER_OTHER_FACTION = -400                  -- vanilla -200

-- Desperate AI. The weak-unit band widens enormously, so a battered army
-- keeps attacking instead of standing off, and it gives up waiting to regain
-- organisation after 60 hours rather than 120.
NDefines.NAI.DESPERATE_AI_WEAK_UNIT_STR_LIMIT = 0.90            -- vanilla 0.35
NDefines.NAI.DESPERATE_ATTACK_WITHOUT_ORG_WHEN_NO_ORG_GAIN = 60 -- vanilla 120

-- Trade: it will commit a larger share of a resource per civilian factory,
-- and tolerates a deal delivering 70% before cancelling rather than 80%.
NDefines.NAI.MINIMUM_GOOD_TRADE_RATIO_PER_CIV = 0.025           -- vanilla 0.005
NDefines.NAI.MIN_DELIVERED_TRADE_FRACTION = 0.70                -- vanilla 0.8

-- Peace conferences: AIs stop deadlocking against each other over the same
-- claim, folding after twenty turns instead of two.
NDefines.NAI.PEACE_BID_FOLD_TURNS_AGAINST_OTHER_AI = 20         -- vanilla 2


-- Held back: the remaining global rules from these groups - world tension
-- rates, embargo weights, wargoal costs, collaboration surrender reduction,
-- convoy ranges, trade distance, collateral damage, river crossing penalties,
-- and the peace score scale and distribution table. All change the rules for
-- you as much as the AI.
-- NDefines.NDiplomacy.WARGOAL_VERSUS_MAJOR_AT_WAR_REDUCTION = -0.80  -- vanilla -0.75
-- NDefines.NDiplomacy.TENSION_JOIN_ATTACKER = 0.25                  -- vanilla 2
-- NDefines.NDiplomacy.TENSION_FACTION_JOIN = 2                      -- vanilla 4
-- NDefines.NDiplomacy.TENSION_VOLUNTEER_FORCE_DIVISION = 0          -- vanilla 0.2
-- NDefines.NDiplomacy.OPINION_FOR_DEMO_FROM_WT_GENERATION = -0.5    -- vanilla -2.0
-- NDefines.NDiplomacy.EMBARGO_NEIGHBOUR_AI_WEIGHT = -50             -- vanilla -10
-- NDefines.NDiplomacy.WARGOAL_COST_DOCKING_RIGHTS = -0.25           -- vanilla -0.2
-- NDefines.NCountry.SURRENDER_LIMIT_REDUCTION_PER_COLLABORATION = 0.20  -- vanilla 0.15
-- NDefines.NTrade.DISTANCE_TRADE_FACTOR = 0                        -- vanilla -0.02
-- NDefines.NTrade.RELATION_TRADE_FACTOR = 1.1                      -- vanilla 1
-- NDefines.NTrade.ANTI_MONOPOLY_TRADE_FACTOR = 0                   -- vanilla -100
-- NDefines.NCountry.CONVOY_RANGE_FACTOR = 0.45                     -- vanilla 1
-- NDefines.NCountry.CONVOY_LENDLEASE_RANGE_FACTOR = 0.45           -- vanilla 1
-- NDefines.NCountry.CONVOY_INTERNATIONAL_MARKET_RANGE_FACTOR = 0.45 -- vanilla 1
-- NDefines.NMilitary.LAND_COMBAT_COLLATERAL_FORT_FACTOR = 0.01     -- vanilla 0.005
-- NDefines.NMilitary.LAND_COMBAT_COLLATERAL_INFRA_FACTOR = 0.003   -- vanilla 0.0022
-- NDefines.NMilitary.RIVER_CROSSING_PENALTY_LARGE = -0.50          -- vanilla -0.6
-- NDefines.NDiplomacy.PEACE_SCORE_SCALE_FACTOR = 1.55              -- vanilla 1.35
-- NDefines.NIndustrialOrganisation.FUNDS_FOR_RESEARCH_COMPLETION_PER_RESEARCH_COST = 750  -- vanilla 500
