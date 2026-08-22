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

## A note on `descriptor.mod`

The required DLC are deliberately **not** listed in the `dependencies` block of
`descriptor.mod`. That field means "other mods that must load before this one" - it is
not a way to require DLC, and there is no descriptor field that is. Listing DLC names
there makes the Paradox Launcher hunt for mods by those names, fail to find them, and
show a warning triangle on the mod for every subscriber.

DLC requirements belong here and in the Workshop description instead.
