Icon molds for the metal industry (tools/gen_metal_industry.py).

Paint over these PNGs, keep the size and the transparent corners,
then run:  python tools/gen_metal_industry.py

building_<metal>.png  46x46  construction menu and state view icon,
                             and also the tech tree icon:
                             steel -> Metal Working Plants I-III,
                             chromium/tungsten -> their Working I-III.
tech_<family>.png     64x64  OPTIONAL: drop one in (family = metal,
                             chromium or tungsten) to give that tech
                             line its own art instead.

Deleting a building mold makes the script recreate a tinted placeholder.
