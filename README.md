# Welt in Flammen

An alternative history mod for Hearts of Iron IV, centred on the Reichskommissariats
and the war in the east.

## Required DLC

This mod needs all three of the following. Without them the content that depends on
them will not appear, and parts of the mod will not work as intended:

| DLC | What the mod uses it for |
| --- | --- |
| **Götterdämmerung** | Reichskommissariat mechanics and the German-controlled / locally-controlled Reichskommissariat spirits the mod builds on |
| **Arms Against Tyranny** | Military Industrial Organisations (`common/military_industrial_organization/`) |
| **La Résistance** | Occupation laws, resistance and compliance (`common/occupation_laws/`) |

Supported game version: **1.19.2**

## Compatibility: Germany Rework (Workshop 3607227153)

Germany Rework ships `common/national_focus/germany.txt` with the focus tree id
`german_focus` - the same filename and the same id this mod uses. Hearts of Iron IV
loads only one file per path, so exactly one German tree is ever active:

- **Germany Rework enabled, ordered after Welt in Flammen** - Germany gets the
  Germany Rework tree.
- **Germany Rework disabled** - Germany gets this mod's tree.

Put Germany Rework **below** Welt in Flammen in the playset; further down loads later
and wins. There is no `has_mod` trigger in Hearts of Iron IV, and `has_focus_tree`
cannot separate the two because both trees answer to `german_focus`, so load order is
the only lever - and it already produces exactly the behaviour above.

Running both: this mod references 163 focus ids outside its own tree, and 154 of them
also exist in the Germany Rework tree, so the overwhelming majority of the German
content keeps working. Nine are Götterdämmerung-era focuses Germany Rework does not
include (`GER_oppose_hitler`, `GER_aging_fuhrer`, `GER_ally_the_shade`,
`GER_pool_technical_know_how`, `GER_shared_rd_programs`,
`GER_rekindle_imperial_sentiment`, `GER_tackle_the_communist_threat`, and two already
commented out). Those checks simply return false, so the affected branches never fire.

This is **not** worth patching around, and the mod deliberately does not try. Vanilla's
own files reference the same focuses more than thirty times over, and those files load
whatever mods are active - so the dangling references exist for anyone running Germany
Rework at all, with or without this mod.

## A note on `descriptor.mod`

The required DLC are deliberately **not** listed in the `dependencies` block of
`descriptor.mod`. That field means "other mods that must load before this one" - it is
not a way to require DLC, and there is no descriptor field that is. Listing DLC names
there makes the Paradox Launcher hunt for mods by those names, fail to find them, and
show a warning triangle on the mod for every subscriber.

DLC requirements belong here and in the Workshop description instead.
