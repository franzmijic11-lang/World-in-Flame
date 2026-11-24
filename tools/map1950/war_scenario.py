"""One imagined run of the First West Russian War, scored by the mod's own rules
(common/scripted_effects/zz_wif_sme_c_war.txt, city table in tools/gen_sme_collapse.py).
Writes war.json for patch_planner.py."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = r'C:\Users\franz\OneDrive\Skrivbord\Dokument\Paradox Interactive\Hearts of Iron IV\mod\Welt_in_Flammen'
src = open(os.path.join(MOD, 'tools', 'gen_sme_collapse.py'), encoding='utf-8').read()
body = src[src.index('CITIES = {'):]
body = body[:body.index('\n}') + 2]
CITIES = {int(a): int(b) for a, b in re.findall(r'(\d+): (\d+)', body)}

states = {s['id']: s for s in json.load(open(os.path.join(HERE, 'states.json'), encoding='utf-8'))}
owner = {i: s['o'] for i, s in states.items()}
OST = ['RKO', 'RKU', 'RKM', 'RKK']
PREWAR = {i for i, o in owner.items() if o == 'SME'}

# (date, kind, args, text)
#   take  (state, taker)      a state changes controller
#   cap   (tag,)              an Ostschild member capitulates
#   idle  ()                  40 days without an SME gain
#   lead  (tag,)              the Ostschild changes leader
#   note  ()                  news only
#   win   ()                  the SME wins
S = 'SME'
EV_SME = [
    ('1952-03-03', 'note', (), "Contact Lost with Germania. Kaukasien, Moskowien, Ukraine and Ostland are cut loose from a Reich at war with itself and form the Ostschild under Ostland. That same night the SME crosses the Volga."),
    ('1952-03-19', 'take', (250, S), "Ulyanovsk falls in the first week of the thaw. The SME's Volga flotilla shells the Moskowien garrison out of the river port."),
    ('1952-03-28', 'take', (255, S), "Penza. The Reichskommissariat's police battalions were never meant to hold a front."),
    ('1952-04-06', 'take', (248, S), "Yaroslavl falls to a northern pincer out of Vologda. The road to Moscow from the north-east is open."),
    ('1952-04-15', 'take', (253, S), "Ivanovo's textile mills change hands without a shot; the workers open the gates."),
    ('1952-04-24', 'take', (239, S), "Saratov. The SME now holds both banks of the middle Volga."),
    ('1952-05-10', 'take', (257, S), "Tambov."),
    ('1952-05-22', 'take', (248, 'RKM'), "The Ostschild strikes back. Ostland's armoured reserve and two Ukrainian divisions retake Yaroslavl. The SME pays double for a city it could not hold."),
    ('1952-06-05', 'take', (254, S), "Ryazan, on the Oka. Moscow is 200 kilometres away."),
    ('1952-06-20', 'take', (258, S), "Lipetsk."),
    ('1952-06-27', 'take', (265, S), "Mikhaylovka, on the Don bend."),
    ('1952-07-02', 'take', (252, 'RKM'), "Disaster: a Moskowien mechanised group slips through the Oka marshes and takes Gorky behind the SME's front. The SME's own city is lost."),
    ('1952-07-18', 'take', (252, S), "Gorky is retaken after two weeks of street fighting. The raiders are destroyed in the Volga bend."),
    ('1952-08-01', 'take', (248, S), "Yaroslavl falls again, this time for good."),
    ('1952-08-14', 'take', (223, S), "Tula and its arms works."),
    ('1952-08-30', 'take', (205, S), "Kaluga. Moscow is surrounded on three sides."),
    ('1952-09-28', 'take', (219, S), "MOSCOW FALLS. The red flag goes back up over the Kremlin for the first time since the surrender. Moskowien's government flees to Smolensk."),
    ('1952-10-05', 'take', (247, S), "Kalinin."),
    ('1952-10-09', 'take', (246, S), "Rzhev."),
    ('1952-10-20', 'take', (217, S), "Stalingrad, again. Moskowien's Volga line is gone."),
    ('1952-10-31', 'take', (260, S), "Voronezh."),
    ('1952-12-10', 'idle', (), "Winter. The front freezes from Lake Ilmen to the Don. Forty days without a gain - the SME's commissars report the men are tired."),
    ('1953-01-12', 'take', (264, S), "Tikhvin. The northern offensive towards Leningrad begins on the ice."),
    ('1953-01-20', 'take', (244, S), "Volkhov."),
    ('1953-02-03', 'take', (195, S), "Leningrad falls to the SME. After a decade under German rule, the city is Russian again."),
    ('1953-02-11', 'take', (263, S), "Novgorod."),
    ('1953-02-20', 'cap', ('RKM',), "MOSKOWIEN CAPITULATES. Its last ministers surrender at Smolensk. Ostland, Ukraine and Kaukasien fight on."),
    ('1953-03-08', 'take', (236, S), "Astrakhan. The SME swings south towards the Caucasus."),
    ('1953-03-15', 'take', (237, S), "Elista and the Kalmyk steppe."),
    ('1953-04-02', 'take', (218, S), "Rostov-on-Don. The gateway to the Caucasus."),
    ('1953-04-20', 'take', (260, 'RKU'), "Ukraine's spring counteroffensive retakes Voronezh..."),
    ('1953-04-24', 'take', (218, 'RKU'), "...and Rostov. Two cities lost, both paid double."),
    ('1953-05-09', 'take', (234, S), "Krasnodar falls to a thrust down the Kuban."),
    ('1953-05-16', 'take', (821, S), "Grozny and its oil."),
    ('1953-05-24', 'take', (232, S), "Makhachkala. The Caspian coast is the SME's."),
    ('1953-05-30', 'take', (242, S), "Smolensk, held by Ostland's divisions since Moskowien's surrender."),
    ('1953-06-04', 'take', (224, S), "Bryansk."),
    ('1953-06-07', 'take', (222, S), "Orel."),
    ('1953-06-12', 'take', (220, S), "Kursk."),
    ('1953-06-15', 'take', (229, S), "BAKU. Kaukasien's oil is in Soviet hands."),
    ('1953-06-24', 'take', (230, S), "Yerevan."),
    ('1953-07-01', 'take', (231, S), "Tiflis falls."),
    ('1953-07-01', 'cap', ('RKK',), "KAUKASIEN CAPITULATES."),
    ('1953-07-02', 'win', (), "With Moskowien and Kaukasien both beaten, the war is won. The SME annexes both Reichskommissariate and makes peace with Ukraine and Ostland. What becomes of them is for another war."),
]


# ---------------------------------------------------------------- run 2: the Ostschild's narrow victory
EV_OST = [
    ('1952-03-03', 'note', (), "Contact Lost with Germania. The Ostschild forms under Ostland, and the SME crosses the Volga expecting a short war against leaderless garrisons."),
    ('1952-03-20', 'take', (250, S), "Ulyanovsk falls at once."),
    ('1952-04-02', 'take', (255, S), "Penza."),
    ('1952-04-10', 'take', (239, S), "Saratov."),
    ('1952-04-25', 'take', (248, S), "Yaroslavl."),
    ('1952-05-12', 'take', (254, S), "Ryazan. Zhukov's staff draw the arrows straight at Moscow."),
    ('1952-06-01', 'take', (223, S), "Tula and its arms works."),
    ('1952-06-20', 'take', (219, S), "MOSCOW FALLS. The SME's tanks reach the Kremlin - at the end of a salient 400 kilometres deep, with open flanks on both sides."),
    ('1952-07-05', 'take', (223, 'RKU'), "The counterstroke. Ukraine's divisions, the best-equipped the Reich left behind, cut the salient at Tula."),
    ('1952-07-12', 'take', (254, 'RKO'), "Ostland's armour closes the ring at Ryazan."),
    ('1952-07-28', 'take', (219, 'RKM'), "MOSCOW IS RETAKEN. Three SME armies are trapped east of the city. A city lost costs double - Moscow most of all."),
    ('1952-08-10', 'take', (248, 'RKM'), "Yaroslavl falls back to Moskowien."),
    ('1952-08-20', 'take', (351, 'RKO'), "Ostland's northern group crosses into the SME's own land and takes Vologda."),
    ('1952-09-30', 'idle', (), "The SME's offensives have stopped dead. Forty days without a gain."),
    ('1952-10-02', 'take', (351, S), "Vologda is retaken by militia from the Kotlas works."),
    ('1952-10-20', 'take', (239, 'RKK'), "Kaukasien's cossack corps comes up the Volga and retakes Saratov."),
    ('1952-11-22', 'take', (401, 'RKK'), "The cossacks cross into the SME's heartland and take Balakovo."),
    ('1952-12-31', 'idle', (), "Winter. Nothing moves - and the SME, which must win, is losing by standing still."),
    ('1953-01-20', 'take', (401, S), "The SME's winter offensive throws the cossacks out of Balakovo."),
    ('1953-02-05', 'take', (223, S), "Tula falls again - the SME's last good news of the war."),
    ('1953-02-28', 'note', (), "The Ostschild is near the end too. Moskowien is close to capitulation, Ukraine has no reserves left, and Ostland's leaders talk of a separate peace."),
    ('1953-03-10', 'take', (223, 'RKM'), "Tula is lost again, at double the price."),
    ('1953-03-25', 'take', (252, 'RKM'), "GORKY FALLS. Moskowien's last mobile group - eleven worn-out battalions - takes the SME's second city in a night attack."),
    ('1953-03-26', 'lose', (), "The SME's war is lost. A scripted peace: the Ostschild keeps every SME state it holds and gives back nothing it lost. It won by days - Moskowien would not have lasted the spring."),
] + [(d, 'break', (tag,), txt) for d, tag, txt in [
    ('1953-03-28', 'RUE', 'The Russian Empire is proclaimed in Kirov.'),
    ('1953-03-29', 'VGD', 'Vologda declares itself a neutral state.'),
    ('1953-03-31', 'ZWF', "The Zhukov split: Zhukov marches north with the army's loyal core."),
    ('1953-04-01', 'OSG', 'The Orthodox Order of Saint George takes Gayny.'),
    ('1953-04-03', 'KMR', 'The Free Republic of Komi.'),
    ('1953-04-04', 'ARB', 'The Aryan Brotherhood seizes Perm.'),
    ('1953-04-06', 'RNS', 'The Russian National State in the Central Urals.'),
    ('1953-04-07', 'RFS', 'The Russian Fascist State in Kuybyshev.'),
    ('1953-04-09', 'SPT', 'The Syndicalist State of the True Proletariat in Orenburg. What is left of the SME is a rump on the Volga.'),
]]

BREAKUP_STEPS = lambda start: [(d, 'break', (tag,), txt) for d, tag, txt in [
    (start[0], 'RUE', 'The Russian Empire is proclaimed in Kirov.'),
    (start[1], 'VGD', 'Vologda declares itself a neutral state.'),
    (start[2], 'GRK', 'The Gorky Soviet Republic.'),
    (start[3], 'ZWF', "The Zhukov split: Zhukov marches north with the army's loyal core."),
    (start[4], 'OSG', 'The Orthodox Order of Saint George takes Gayny.'),
    (start[5], 'KMR', 'The Free Republic of Komi.'),
    (start[6], 'ARB', 'The Aryan Brotherhood seizes Perm.'),
    (start[7], 'RNS', 'The Russian National State in the Central Urals.'),
    (start[8], 'RFS', 'The Russian Fascist State in Kuybyshev.'),
    (start[9], 'SPT', 'The Syndicalist State of the True Proletariat in Orenburg. What is left of the SME is a rump on the Volga.'),
]]

# ---------------------------------------------------------------- run 3: the battles for Moscow
EV_MOSCOW = [
    ('1952-03-03', 'note', (), "Contact Lost with Germania. The Ostschild forms under Ostland. Neither side is strong enough to finish the other."),
    ('1952-03-25', 'take', (250, S), "Ulyanovsk."),
    ('1952-04-10', 'take', (255, S), "Penza."),
    ('1952-04-28', 'take', (248, S), "Yaroslavl."),
    ('1952-05-20', 'take', (254, S), "Ryazan."),
    ('1952-06-15', 'take', (223, S), "Tula."),
    ('1952-07-10', 'take', (205, S), "Kaluga. Moscow is in reach."),
    ('1952-08-05', 'take', (219, S), "THE FIRST BATTLE OF MOSCOW. The SME takes the city after three weeks of street fighting."),
    ('1952-08-30', 'take', (219, 'RKM'), "THE SECOND BATTLE OF MOSCOW. Moskowien and Ostland retake it from the west. The SME pays double."),
    ('1952-09-25', 'take', (219, S), "THE THIRD BATTLE OF MOSCOW. The SME is back in the Kremlin."),
    ('1952-10-20', 'take', (247, S), "Kalinin."),
    ('1952-11-15', 'take', (219, 'RKO'), "THE FOURTH BATTLE OF MOSCOW. Ostland's armour drives the SME out of a city that is mostly rubble now."),
    ('1952-12-25', 'idle', (), "The first winter. Both armies dig in around the ruins."),
    ('1953-01-30', 'take', (223, 'RKU'), "Ukraine's winter offensive retakes Tula."),
    ('1953-03-05', 'take', (219, S), "THE FIFTH BATTLE OF MOSCOW. The SME takes it again."),
    ('1953-03-20', 'take', (223, S), "Tula, again."),
    ('1953-04-15', 'take', (219, 'RKM'), "THE SIXTH BATTLE OF MOSCOW. Moskowien's guards divisions retake the city block by block."),
    ('1953-05-10', 'take', (247, 'RKO'), "Kalinin is lost."),
    ('1953-06-01', 'take', (248, 'RKM'), "Yaroslavl is lost."),
    ('1953-06-20', 'take', (248, S), "Yaroslavl is retaken three weeks later."),
    ('1953-07-15', 'idle', (), "A summer of shelling and no movement."),
    ('1953-08-10', 'take', (219, S), "THE SEVENTH BATTLE OF MOSCOW. The SME takes the ruins one last time."),
    ('1953-09-05', 'take', (219, 'RKM'), "THE EIGHTH BATTLE OF MOSCOW. The SME's last reserves are spent in the city; it falls back to Moskowien for good."),
    ('1953-10-01', 'take', (254, 'RKO'), "Ryazan."),
    ('1953-10-20', 'take', (223, 'RKU'), "Tula."),
    ('1953-11-15', 'take', (254, S), "The SME's last counterattack retakes Ryazan."),
    ('1953-12-20', 'idle', (), "The second winter. The SME's divisions are a third of their strength."),
    ('1954-01-25', 'take', (205, 'RKM'), "Kaluga."),
    ('1954-02-15', 'take', (248, 'RKO'), "YAROSLAVL FALLS. The SME's northern front breaks, and with it the will to go on."),
    ('1954-02-16', 'lose', (), "The SME's war is lost. Two years and eight battles for Moscow later, the Ostschild has won the war of attrition, barely. A scripted peace: each side keeps what it holds of the other's land, and the SME gives back what it took."),
] + BREAKUP_STEPS(['1954-02-18', '1954-02-19', '1954-02-21', '1954-02-22', '1954-02-24', '1954-02-25', '1954-02-27', '1954-02-28', '1954-03-02', '1954-03-04'])

# ---------------------------------------------------------------- run 4: holding on until the Reich returns
EV_REICH = [
    ('1952-03-03', 'note', (), "Contact Lost with Germania. The Ostschild forms under Ostland and has one hope: to hold out until the Reich puts itself back together."),
    ('1952-03-20', 'take', (250, S), "Ulyanovsk."),
    ('1952-04-05', 'take', (255, S), "Penza."),
    ('1952-04-18', 'take', (239, S), "Saratov."),
    ('1952-05-02', 'take', (248, S), "Yaroslavl."),
    ('1952-05-20', 'take', (253, S), "Ivanovo."),
    ('1952-06-10', 'take', (254, S), "Ryazan."),
    ('1952-07-01', 'take', (223, S), "Tula."),
    ('1952-07-25', 'take', (205, S), "Kaluga."),
    ('1952-08-20', 'take', (219, S), "MOSCOW FALLS. Moskowien's government flees to Smolensk."),
    ('1952-09-15', 'take', (247, S), "Kalinin."),
    ('1952-10-10', 'take', (217, S), "Stalingrad."),
    ('1952-11-05', 'take', (260, S), "Voronezh."),
    ('1952-12-01', 'take', (257, S), "Tambov."),
    ('1953-01-20', 'take', (264, S), "Tikhvin."),
    ('1953-02-15', 'take', (258, S), "Lipetsk."),
    ('1953-03-01', 'note', (), "The Ostschild holds a last line from Lake Ilmen through Smolensk, Bryansk and Kursk to the Don. Moskowien is close to capitulation. Every week counts."),
    ('1953-03-20', 'take', (218, S), "Rostov."),
    ('1953-04-10', 'take', (236, S), "Astrakhan."),
    ('1953-05-01', 'take', (218, 'RKU'), "A Ukrainian counterattack retakes Rostov."),
    ('1953-06-01', 'take', (195, S), "Leningrad falls."),
    ('1953-06-20', 'take', (263, S), "Novgorod."),
    ('1953-07-10', 'idle', (), "The line on the Lovat holds. Forty days without an SME gain."),
    ('1953-08-15', 'take', (234, S), "Krasnodar."),
    ('1953-09-01', 'take', (821, S), "Grozny."),
    ('1953-10-05', 'take', (260, 'RKU'), "Voronezh is retaken."),
    ('1953-11-20', 'idle', (), "The front freezes at Smolensk. Moskowien's ministers count the days."),
    ('1954-01-15', 'reunify', (), "THE REICH REUNITES under Hermann Goring as the Greater German Reich, and declares war on the SME. The Ostschild joins the Axis. From now on the SME loses 5 points a month."),
    ('1954-02-01', 'month', (), "The first Wehrmacht divisions reach Smolensk by rail."),
    ('1954-02-20', 'take', (195, 'GER'), "German troops retake Leningrad."),
    ('1954-03-01', 'month', (), "A month of the Reich at war."),
    ('1954-03-15', 'take', (263, 'GER'), "Novgorod."),
    ('1954-04-01', 'month', (), "German panzer armies assemble west of Moscow."),
    ('1954-04-10', 'take', (219, 'GER'), "MOSCOW IS RETAKEN by German and Moskowien troops together."),
    ('1954-04-28', 'take', (247, 'GER'), "Kalinin."),
    ('1954-05-01', 'month', (), "A month of the Reich at war."),
    ('1954-05-12', 'take', (223, 'GER'), "Tula."),
    ('1954-05-25', 'take', (217, 'GER'), "Stalingrad."),
    ('1954-06-01', 'month', (), "A month of the Reich at war."),
    ('1954-06-10', 'take', (234, 'RKK'), "Kaukasien, with German air support, retakes Krasnodar."),
    ('1954-06-20', 'take', (254, 'GER'), "Ryazan."),
    ('1954-07-01', 'month', (), "A month of the Reich at war."),
    ('1954-07-08', 'take', (248, 'GER'), "Yaroslavl."),
    ('1954-07-20', 'take', (821, 'RKK'), "Grozny."),
    ('1954-08-01', 'month', (), "A month of the Reich at war."),
    ('1954-08-12', 'take', (252, 'GER'), "GORKY FALLS to the German panzers."),
    ('1954-08-13', 'lose', (), "The SME's war is lost. The Ostschild survived - but only because the Reich came back for it."),
    ('1954-08-15', 'rk', (), "The Ostschild dissolves. Ostland, Ukraine, Moskowien and Kaukasien become Reichskommissariate of the reunited Reich again, and the land the Wehrmacht took goes back to them."),
] + BREAKUP_STEPS(['1954-08-17', '1954-08-18', '1954-08-20', '1954-08-21', '1954-08-23', '1954-08-24', '1954-08-26', '1954-08-27', '1954-08-29', '1954-08-31'])

# ---------------------------------------------------------------- the German civil war (zz_wif_ger_collapse.txt)
# Who declares where, as the mod splits the Reich. The winner was drawn at random from
# everyone but the SS Remnant: Goring.
GCW_SPLIT = {
    'SSR': [42, 978, 28, 8],
    'BOR': [64, 62, 65, 68, 63, 66, 67, 60, 61],
    'GOR': [4, 152, 153, 848, 975, 976, 52, 53, 54, 50, 972],
    'SPG': [51, 55, 59, 56, 58, 909, 912, 57],
    'BMP': [9, 75, 69, 74],
    'DWM': [5, 763, 85, 86, 87, 97, 98, 762, 807, 72],
    'GAG': [102, 127, 144, 192, 198, 829, 834],
}
GCW_C = {'SSR': ('SS Remnant', '#1d1d1f'), 'BOR': ("Bormann's German Reich", '#7a3b34'), 'GOR': ("Goring's Germany", '#456a9e'),
         'SPG': ("Speer's Germany", '#c29a2a'), 'DWM': ('Deutsche Wehrmacht', '#6f7d4a'),
         'BMP': ('Protectorate of Bohemia and Moravia', '#dec488'), 'GAG': ('German Administrative Government (Oslo)', '#60687a')}
EV_GCW = [
    ('1952-02-24', 'gsplit', (), "THE REICH FALLS APART. The Fuhrer is dead and the Reich splits five ways: Bormann in Berlin, Goring in Munich, Speer in the Ruhr, the Wehrmacht generals in the east and the SS on the Rhine. Donitz governs what is left abroad from Oslo."),
    ('1952-04-15', 'gcw', ([978, 'GOR'],), "German civil war: Goring's army takes Baden from the SS."),
    ('1952-05-30', 'gcw', ([59, 'BOR'],), "German civil war: Bormann takes Hannover from Speer."),
    ('1952-06-20', 'gcw', ([66, 'DWM'],), "German civil war: the Wehrmacht takes Lower Silesia from Bormann."),
    ('1952-08-10', 'gcw', ([42, 'GOR'], [28, 'GOR'], [8, 'GOR']), "German civil war: Goring's Luftwaffe breaks the SS on the Rhine."),
    ('1952-08-12', 'gann', ('SSR', 'GOR'), "German civil war: the SS Remnant is destroyed. Goring annexes the Rhine."),
    ('1952-09-05', 'gcw', ([59, 'SPG'],), "German civil war: Speer retakes Hannover."),
    ('1952-10-12', 'gcw', ([60, 'GOR'],), "German civil war: Goring takes Thuringia from Bormann."),
    ('1953-01-15', 'gcw', ([65, 'GOR'],), "German civil war: Goring takes Saxony."),
    ('1953-03-10', 'gcw', ([64, 'GOR'],), "German civil war: BERLIN FALLS to Goring. Bormann is captured in the Reich Chancellery."),
    ('1953-03-11', 'gann', ('BOR', 'GOR'), "German civil war: Bormann's German Reich is annexed by Goring."),
    ('1953-05-02', 'gcw', ([67, 'GOR'], [66, 'GOR']), "German civil war: Goring drives the Wehrmacht out of Silesia."),
    ('1953-06-20', 'gann', ('SPG', 'GOR'), "German civil war: Speer surrenders the Ruhr to Goring in return for his life and his ministry."),
    ('1953-10-15', 'gcw', ([86, 'GOR'], [85, 'GOR'], [807, 'GOR']), "German civil war: Poznan and Danzig fall to Goring."),
    ('1953-12-01', 'gann', ('DWM', 'GOR'), "German civil war: the Wehrmacht generals surrender at Konigsberg."),
    ('1953-12-20', 'gann', ('BMP', 'GOR'), "German civil war: the Protectorate is folded back into Goring's Reich."),
    ('1954-01-10', 'gann', ('GAG', 'GOR'), "German civil war: Donitz's Oslo government accepts Goring. The civil war is over."),
]
EV_REICH = sorted(EV_REICH + EV_GCW, key=lambda e: e[0])


def shift(EV, after, days, keep=()):
    """Every event after `after` comes `days` later - the Ostschild's reserves are in Ukraine."""
    import datetime
    out = []
    for e in EV:
        if e[0] > after and e[1] not in keep:
            d = datetime.date.fromisoformat(e[0]) + datetime.timedelta(days=days)
            e = (d.isoformat(),) + e[1:]
        out.append(e)
    return out


def merge(EV, extra):
    return sorted(EV + extra, key=lambda e: e[0])


UPRISING_TEXT = ("UKRAINE RISES. With Moscow lost, the Reichskommissariat comes apart. The Republic of Ukraine is proclaimed in Chernigov, Sumy and Poltava, "
                 "the Ukrainian Socialist Republic in the Donbas, a National Farmers State in Mykolaiv{}. Their militias are green and their rifles a generation old, "
                 "but every city they hold counts for the SME.")

# 1. SME victory: the rising makes it quicker.
EV_SME = [e for e in EV_SME if not ('Ukraine' in e[3] and 'counteroffensive' in e[3]) and not e[3].startswith('...and Rostov')]
EV_SME = merge(EV_SME, [
    ('1952-09-30', 'ukr', (False,), UPRISING_TEXT.format(', and the Ukrainian National State in Proskuriv')),
    ('1952-11-12', 'take', (221, 'UKS'), "The Socialists' Donbas militias take Kharkov."),
    ('1952-12-20', 'take', (226, 'UKS'), "Dnipropetrovsk falls to the Socialists."),
    ('1953-01-05', 'take', (259, 'RKU'), "Koch's colonial police retake Poltava. The Ukrainians lose only what the city is worth."),
    ('1953-01-25', 'take', (202, 'UKR'), "The Republic's columns march into Kiev. Koch flees to Rowno."),
    ('1953-02-12', 'take', (203, 'UKR'), "Cherkasy."),
    ('1953-03-04', 'take', (259, 'UKR'), "Poltava is retaken by the Republic."),
    ('1953-03-18', 'cap', ('RKU',), "REICHSKOMMISSARIAT UKRAINE CAPITULATES. Koch surrenders at Rowno."),
    ('1953-03-19', 'rkufall', ('UKR',), "The partisans cut Ukraine up: each keeps what its militias hold, and everything else goes to the Republic, which did most to bring Koch down."),
    ('1953-03-24', 'unify', ('UKR', ['UKS', 'UFS', 'UNS']), "The Republic of Ukraine is the largest of the new governments. Nobody objects to the Republic: the Socialists, the Farmers and the Nationalists all join it."),
])

# 2. The Ostschild does everything right: Ukraine is crushed first, and the war takes longer.
EV_OST = shift(EV_OST, '1952-06-20', 150)
EV_OST = merge(EV_OST, [
    ('1952-06-22', 'ukr', (True,), UPRISING_TEXT.format(". In Proskuriv the nationalists stay loyal to Koch - he had chosen to use them")),
    ('1952-07-20', 'take', (227, 'RKU'), "Koch's police and Ostland's armour storm Stalino. The Ukrainians lose only what the city is worth."),
    ('1952-08-10', 'take', (200, 'RKU'), "Zaporozhe."),
    ('1952-08-11', 'ucrush', ('UKS', 'RKU'), "The Ukrainian Socialist Republic is crushed."),
    ('1952-09-01', 'take', (247, S), "With the Ostschild's reserves in Ukraine, the SME takes Kalinin."),
    ('1952-09-14', 'take', (197, 'RKU'), "Mykolaiv."),
    ('1952-09-15', 'ucrush', ('UFS', 'RKU'), "The Farmers State is crushed."),
    ('1952-10-05', 'take', (259, 'RKU'), "Poltava."),
    ('1952-10-30', 'take', (260, S), "The SME takes Voronezh."),
    ('1952-11-01', 'take', (225, 'RKU'), "Sumy."),
    ('1952-11-20', 'take', (193, 'RKU'), "Chernigov."),
    ('1952-11-21', 'ucrush', ('UKR', 'RKU'), "The Republic of Ukraine is crushed. Ukraine is quiet - for now - and the Ostschild's armies turn north."),
    ('1952-11-22', 'note', (), "In Proskuriv the nationalist auxiliaries are disarmed at dawn. Their officers are shot. They were never allies."),
    ('1953-01-28', 'take', (247, 'RKO'), "Kalinin is retaken."),
    ('1953-03-20', 'take', (260, 'RKU'), "Voronezh is retaken."),
])

# 3. The battles for Moscow: a second front in Ukraine, and a longer grind.
EV_MOSCOW = shift(EV_MOSCOW, '1952-12-01', 120)
EV_MOSCOW = merge(EV_MOSCOW, [
    ('1952-08-07', 'ukr', (False,), UPRISING_TEXT.format(', and the Ukrainian National State in Proskuriv')),
    ('1952-10-10', 'take', (221, 'UKS'), "The Socialists take Kharkov."),
    ('1952-11-25', 'take', (226, 'UKS'), "Dnipropetrovsk."),
    ('1953-01-15', 'take', (259, 'RKU'), "Koch's police retake Poltava."),
    ('1953-02-10', 'take', (226, 'RKU'), "Dnipropetrovsk is retaken."),
    ('1953-03-01', 'take', (221, 'RKU'), "Kharkov is retaken after a month of street fighting."),
    ('1953-03-15', 'take', (227, 'RKU'), "Stalino."),
    ('1953-03-28', 'take', (200, 'RKU'), "Zaporozhe."),
    ('1953-03-29', 'ucrush', ('UKS', 'RKU'), "The Ukrainian Socialist Republic is crushed."),
    ('1953-04-20', 'take', (199, 'RKU'), "Proskuriv."),
    ('1953-04-21', 'ucrush', ('UNS', 'RKU'), "The Ukrainian National State is crushed."),
    ('1953-05-12', 'take', (197, 'RKU'), "Mykolaiv."),
    ('1953-05-13', 'ucrush', ('UFS', 'RKU'), "The Farmers State is crushed."),
    ('1953-06-10', 'take', (225, 'RKU'), "Sumy."),
    ('1953-06-30', 'take', (193, 'RKU'), "Chernigov."),
    ('1953-07-01', 'ucrush', ('UKR', 'RKU'), "The Republic of Ukraine is crushed. A year of fighting in Ukraine is over; Moscow is still burning."),
])

# 4. Holding on until the Reich returns: Ukraine is lost, then retaken by the Reich.
EV_REICH = shift(EV_REICH, '1954-01-15', 75, keep=('month',))
EV_REICH = merge(EV_REICH, [
    ('1952-08-22', 'ukr', (False,), UPRISING_TEXT.format(', and the Ukrainian National State in Proskuriv')),
    ('1952-11-10', 'take', (221, 'UKS'), "The Socialists take Kharkov."),
    ('1953-01-15', 'take', (226, 'UKS'), "Dnipropetrovsk."),
    ('1953-04-02', 'take', (202, 'UKS'), "Kiev falls to the Socialists."),
    ('1953-05-20', 'cap', ('RKU',), "REICHSKOMMISSARIAT UKRAINE CAPITULATES. The Ostschild loses its breadbasket."),
    ('1953-05-21', 'rkufall', ('UKS',), "The partisans cut Ukraine up. Everything no militia holds goes to the Socialists, who did most to bring Koch down."),
    ('1953-05-26', 'unify', ('UKS', ['UFS']), "The Socialists are the largest. The Farmers join them; the Republic and the Nationalists refuse."),
    ('1953-09-01', 'note', (), "The Socialists declare war on the Republic and the National State. Ukraine's civil war begins - with the Reich's civil war nearly over."),
    ('1954-03-01', 'month', (), "German divisions cross into Ukraine."),
    ('1954-03-20', 'take', (227, 'GER'), "German troops take Stalino from the Socialists. The Ukrainians lose only what each city is worth."),
    ('1954-04-05', 'take', (221, 'GER'), "Kharkov."),
    ('1954-04-25', 'take', (202, 'GER'), "Kiev."),
    ('1954-05-15', 'take', (226, 'GER'), "Dnipropetrovsk."),
    ('1954-05-16', 'rkback', ('UKS',), "The Ukrainian Socialist Republic capitulates to the Reich. No peace conference: its land goes straight to a re-established Reichskommissariat Ukraine."),
    ('1954-06-10', 'take', (259, 'GER'), "Poltava."),
    ('1954-06-25', 'take', (225, 'GER'), "Sumy."),
    ('1954-07-05', 'take', (193, 'GER'), "Chernigov."),
    ('1954-07-06', 'rkback', ('UKR',), "The Republic of Ukraine capitulates. Its land goes back to the Reichskommissariat."),
    ('1954-07-30', 'take', (199, 'GER'), "Proskuriv."),
    ('1954-07-31', 'rkback', ('UNS',), "The Ukrainian National State capitulates. Ukraine is a Reichskommissariat again."),
    ('1954-09-01', 'month', (), "A month of the Reich at war."),
    ('1954-10-01', 'month', (), "A month of the Reich at war."),
])


RISING_TEXT = ("THE OSTLAND RISES. With {} in the SME's hands, the Reichskommissariat Ostland comes apart. In the Estonian and Lithuanian woods the "
               "Forest Brothers proclaim a Council of Brothers - Virumaa, Tartu, Zemgale and Aukstaitija - with experienced ranger battalions on Ostland's own rifles. "
               "The Belarusian brigades come out of the marshes and take all six Belarusian states: one green militia division each, for the population is half what it was. "
               "Every city they hold counts for the SME; a city they lose costs only its value.")
ELF_TEXT = ("SWEDEN STRIKES BACK. For years Stockholm has appeased Berlin. Now a democratic Sweden smuggles 1800 rifles to Saaremaa, and the island rises as the "
            "Estonian Liberation Front, three infantry divisions strong.")

# 1. SME victory: Ostland breaks too, and after the war its peoples finish it off.
EV_SME = merge(EV_SME, [
    ('1952-10-05', 'rko', (), RISING_TEXT.format('Kalinin')),
    ('1952-11-02', 'elf', (), ELF_TEXT),
    ('1952-11-20', 'take', (810, 'BLR'), "The Belarusian brigades push north and take Latgale."),
    ('1952-12-15', 'take', (12, 'FBR'), "The Forest Brothers take Vidzeme. Riga is cut off from the east."),
    ('1953-01-08', 'take', (13, 'EST'), "The Estonian Liberation Front crosses to the mainland and takes Parnu."),
    ('1953-01-30', 'take', (11, 'FBR'), "Kaunas falls to the Lithuanian Forest Brothers."),
    ('1953-07-20', 'take', (784, 'FBR'), "With the SME at peace, Ostland stands alone. The Forest Brothers take Vilna."),
    ('1953-08-25', 'take', (808, 'FBR'), "RIGA FALLS to the Forest Brothers."),
    ('1953-08-30', 'cap', ('RKO',), "REICHSKOMMISSARIAT OSTLAND CAPITULATES. Lohse surrenders at Libau."),
    ('1953-08-31', 'rkofall', (), "The Ostland is shared out. The Council of Brothers takes the Baltic and becomes the Baltic Union, with cores on all three nations. Belarus keeps the Belarusian land. The Estonian Liberation Front takes Tallinn - and becomes a supervised state of Sweden."),
])

# 2. The Ostschild does everything right: Ostland crushes both risings, and the war takes longer.
EV_OST = shift(EV_OST, '1952-09-01', 90)
EV_OST = merge(EV_OST, [
    ('1952-09-01', 'rko', (), RISING_TEXT.format('Kalinin')),
    ('1952-09-02', 'note', (), "Sweden watches the Ostschild hold its front - and keeps its rifles."),
    ('1952-09-25', 'take', (206, 'RKO'), "Ostland's armoured reserve turns back and storms Minsk. The partisans lose only what the city is worth."),
    ('1952-10-12', 'take', (95, 'RKO'), "Baranovichi."),
    ('1952-10-30', 'take', (204, 'RKO'), "Bobruysk."),
    ('1952-11-10', 'ocrush', ('BLR', 'RKO'), "Belarus is crushed. The brigades go back into the marshes."),
    ('1952-11-25', 'take', (191, 'RKO'), "Tartu is retaken."),
    ('1952-12-20', 'take', (809, 'RKO'), "Zemgale."),
    ('1953-01-05', 'ocrush', ('FBR', 'RKO'), "The Council of Brothers capitulates. Its rangers vanish into the forests, and Ostland's divisions turn east again."),
])

# 3. The battles for Moscow: Belarus is retaken, the Forest Brothers hold out to the end.
EV_MOSCOW = shift(EV_MOSCOW, '1952-10-20', 60)
EV_MOSCOW = merge(EV_MOSCOW, [
    ('1952-10-20', 'rko', (), RISING_TEXT.format('Kalinin')),
    ('1953-01-10', 'elf', (), ELF_TEXT),
    ('1953-02-01', 'take', (206, 'RKO'), "Ostland retakes Minsk after a month of street fighting."),
    ('1953-03-10', 'take', (204, 'RKO'), "Bobruysk."),
    ('1953-04-05', 'take', (95, 'RKO'), "Baranovichi."),
    ('1953-05-01', 'ocrush', ('BLR', 'RKO'), "Belarus is crushed."),
    ('1953-07-01', 'take', (809, 'RKO'), "Zemgale is retaken from the Forest Brothers."),
    ('1954-06-01', 'take', (811, 'RKO'), "With the SME beaten, Ostland lands on Saaremaa."),
    ('1954-06-02', 'ocrush', ('EST', 'RKO'), "The Estonian Liberation Front capitulates. Sweden's gamble has failed."),
    ('1954-08-10', 'take', (191, 'RKO'), "Tartu."),
    ('1954-09-05', 'ocrush', ('FBR', 'RKO'), "The Council of Brothers capitulates. The forests are quiet - for now."),
])

# 4. Holding on until the Reich returns: Ostland keeps the coast; the Reich clears the rest.
EV_REICH = merge(EV_REICH, [
    ('1952-09-15', 'rko', (), RISING_TEXT.format('Kalinin')),
    ('1952-11-20', 'elf', (), ELF_TEXT),
    ('1952-12-10', 'take', (206, 'RKO'), "Ostland retakes Minsk with its last reserve."),
    ('1953-02-05', 'take', (191, 'RKO'), "Tartu."),
    ('1953-03-20', 'take', (95, 'RKO'), "Baranovichi."),
    ('1953-07-05', 'take', (206, 'BLR'), "Minsk falls to the Belarusian brigades again."),
    ('1954-04-01', 'take', (206, 'GER'), "German troops take Minsk from the Belarusians."),
    ('1954-04-20', 'take', (204, 'GER'), "Bobruysk."),
    ('1954-05-01', 'rkoback', ('BLR',), "Belarus capitulates to the Reich. No peace conference: its land goes straight back to the Reichskommissariat Ostland."),
    ('1954-06-01', 'take', (813, 'GER'), "German troops take Virumaa."),
    ('1954-06-02', 'rkoback', ('FBR',), "The Council of Brothers capitulates to the Reich. Its land goes back to Ostland."),
    ('1954-06-20', 'take', (811, 'GER'), "German marines land on Saaremaa."),
    ('1954-06-21', 'rkoback', ('EST',), "The Estonian Liberation Front capitulates. Sweden's rifles are lying in the sand."),
])

# 5. The Reich takes back the East: run 1, then the German civil war, the Reich's return and its war of revenge.
EV_BACK = EV_SME + EV_GCW + [
    ('1954-01-15', 'reunify', (), "THE REICH REUNITES under Hermann Goring. It finds the East gone: Moskowien and Kaukasien are the SME's, Ukraine and the Baltic are free, Belarus is red and Swedish troops are in Tallinn."),
    ('1954-02-01', 'note', (), "The Reich declares war on every government that rose against the Reichskommissariate."),
    ('1954-02-10', 'note', (), "ULTIMATUM TO SWEDEN: hand back Estonia, or face the Wehrmacht. Stockholm refuses - Sweden will fight."),
    ('1954-03-05', 'take', (206, 'GER'), "German troops take Minsk."),
    ('1954-03-25', 'take', (95, 'GER'), "Baranovichi."),
    ('1954-04-10', 'take', (204, 'GER'), "Bobruysk."),
    ('1954-04-11', 'rkoback', ('BLR',), "Belarus capitulates. Reichskommissariat Ostland is re-established in Minsk - no peace conference."),
    ('1954-05-01', 'take', (202, 'GER'), "Kiev."),
    ('1954-05-20', 'take', (221, 'GER'), "Kharkov."),
    ('1954-06-10', 'take', (227, 'GER'), "Stalino."),
    ('1954-06-11', 'rkback', ('UKR',), "The Republic of Ukraine capitulates. Its land goes straight back to a re-established Reichskommissariat Ukraine."),
    ('1954-07-01', 'take', (808, 'GER'), "RIGA is taken from the Baltic Union."),
    ('1954-07-20', 'take', (11, 'GER'), "Kaunas."),
    ('1954-08-05', 'take', (191, 'GER'), "Tartu."),
    ('1954-08-06', 'rkoback', ('BUN',), "The Baltic Union capitulates. The Baltic goes back to the Reichskommissariat Ostland."),
    ('1954-08-25', 'take', (812, 'GER'), "German troops storm Tallinn. The Swedish brigade fights to the last man."),
    ('1954-09-10', 'take', (811, 'GER'), "Saaremaa."),
    ('1954-09-11', 'rkoback', ('ESW',), "Swedish Estonia capitulates. The war with Sweden ends in a white peace, and Estonia goes back to the Ostland."),
    ('1954-10-01', 'note', (), "THE WAR OF REVENGE. Ostland and Ukraine stand again, and the Reich is whole. Germany and its Reichskommissariate declare war on the SME."),
    ('1954-10-25', 'take', (242, 'GER'), "Smolensk."),
    ('1954-11-20', 'take', (247, 'GER'), "Kalinin."),
    ('1954-12-15', 'take', (195, 'GER'), "Leningrad."),
    ('1955-02-10', 'take', (223, 'GER'), "Tula."),
    ('1955-03-15', 'take', (219, 'GER'), "MOSCOW IS GERMAN AGAIN."),
    ('1955-03-16', 'revwin', (), "The SME makes peace. Reichskommissariat Moskowien and Reichskommissariat Kaukasien are re-established, and the East is the Reich's once more. Beaten a second time, the SME falls apart."),
] + BREAKUP_STEPS(['1955-03-18', '1955-03-19', '1955-03-21', '1955-03-22', '1955-03-24', '1955-03-25', '1955-03-27', '1955-03-28', '1955-03-30', '1955-04-01'])
EV_BACK = sorted(EV_BACK, key=lambda e: e[0])


def fix_seasons(EV):
    """The shifts move some events out of their season: no 'winter' in June."""
    out = []
    for d, k, a, tx in EV:
        m = int(d[5:7])
        if m not in (11, 12, 1, 2, 3):
            tx = re.sub(r'^(The (first|second) winter|Winter)\. ', '', tx)
            tx = tx.replace("'s winter offensive", "'s offensive").replace('The front freezes', 'The front stalls')
        if m not in (6, 7, 8):
            tx = tx.replace('A summer of shelling', 'Months of shelling')
        out.append((d, k, a, tx))
    return out


EV_SME, EV_OST, EV_MOSCOW, EV_REICH, EV_BACK = map(fix_seasons, (EV_SME, EV_OST, EV_MOSCOW, EV_REICH, EV_BACK))

BREAK = {'RUE': [400], 'VGD': [351], 'GRK': [252], 'OSG': [1085], 'KMR': [397, 880, 262, 581], 'ARB': [398],
         'RNS': [1084, 1083, 1082, 399], 'RFS': [251, 401], 'SPT': [652, 582, 651, 573], 'ZWF': [214, 825, 879]}
BREAK_C = {'RUE': ('Russian Empire', '#eede96'), 'VGD': ('Neutral State of Vologda', '#ce483e'), 'GRK': ('Gorky Soviet Republic', '#961c3a'),
           'OSG': ('Orthodox Order of Saint George', '#e4b216'), 'KMR': ('Free Republic of Komi', '#3a966c'), 'ARB': ('Aryan Brotherhood', '#3e3e42'),
           'RNS': ('Russian National State', '#3052aa'), 'RFS': ('Russian Fascist State', '#80681a'), 'SPT': ('Syndicalist State of the True Proletariat', '#de5222'),
           'ZWF': ('West Russian Army Front (Zhukov)', '#761010')}


UKRT = ['UKR', 'UKS', 'UFS', 'UNS']
UPRISE = {'UKR': [193, 225, 259], 'UKS': [227, 200], 'UFS': [197], 'UNS': [199]}
UKR_C = {'UKR': ('Republic of Ukraine', '#e8d34a'), 'UKS': ('Ukrainian Socialist Republic', '#b02222'),
         'UFS': ('Ukrainian National Farmers State', '#96a03c'), 'UNS': ('Ukrainian National State', '#463228')}


RKOT = ['FBR', 'BUN', 'BLR', 'EST', 'ESW']
RISE_FBR = [813, 191, 809, 815]          # the AI goes strict, so Zemgale and Aukstaitija are never cored
RISE_BLR = [206, 204, 194, 94, 95, 96]
BALT = [13, 191, 813, 812, 811, 808, 190, 809, 12, 810, 11, 189, 814, 815, 784]
BELA = RISE_BLR
RKO_C = {'FBR': ('Council of Brothers', '#2f6b4a'), 'BUN': ('Baltic Union', '#5b9a72'), 'BLR': ('Belarus', '#c4602e'),
         'EST': ('Estonian Liberation Front', '#3b74c4'), 'ESW': ('Estonia (Swedish supervised state)', '#78a6e0')}
PART = UKRT + RKOT
WIN_TEXT = "The war score reaches +170: the SME has won. It annexes Moskowien and Kaukasien and makes peace with everyone else. What becomes of Ukraine and Ostland is now for their own peoples - and for the Reich, if it ever comes back."


def run(EV, stop_at_win=False, cont=False):
    score, held, ukr_held, prewar_lost, steps = 5, set(), set(), set(), []
    ctrl, own = dict(owner), dict(owner)
    sme_side = lambda by: by == S or by in PART
    won = frozen = False

    def city(s, by):
        # The SME's score for a city changing hands. The Ukrainians' gains count like the
        # SME's; a city they lose costs only its value, never double (user, 2026-11-24).
        if s in PREWAR or s not in CITIES:
            return 0
        if sme_side(by):
            if by in PART: ukr_held.add(s)
            else: ukr_held.discard(s)
            if s not in held:
                held.add(s); return CITIES[s]
            return 0
        if s in held:
            held.discard(s)
            single = s in ukr_held
            ukr_held.discard(s)
            return -CITIES[s] if single else -2 * CITIES[s]
        return 0

    for date, kind, args, text in EV:
        delta, c, o, out = 0, [], [], []
        if stop_at_win and score >= 170 and not won and kind != 'win':
            wo = [[i, 'SME'] for i, ow in own.items() if ow in ('RKM', 'RKK')]
            for i, _ in wo:
                own[i] = ctrl[i] = 'SME'
            for i in owner:                      # the white peace: occupied land goes back
                if ctrl[i] != own[i] and own[i] not in PART and ctrl[i] not in PART:
                    ctrl[i] = own[i]
            steps.append({'d': date, 'k': 'win', 'c': [], 'o': wo, 'dl': 0, 'sc': score, 'out': ['RKM', 'RKK', '_won'], 't': WIN_TEXT})
            won = frozen = True
            if not cont:
                break
        if won:
            # The SME's war is over: only the risings' wars (and the Reich's) go on.
            if kind in ('win', 'idle', 'lead') or (kind == 'cap' and args[0] in ('RKM', 'RKK')):
                continue
            if kind == 'take' and (args[1] == S or (args[1] in OST and ctrl.get(args[0]) not in PART)):
                continue
        if kind == 'take':
            s, by = args
            c.append([s, by])
            if s in PREWAR:
                if by == S and s in prewar_lost:
                    prewar_lost.discard(s); delta = 40 + (15 if s == 252 else 0)
                elif by != S and s not in prewar_lost:
                    prewar_lost.add(s); delta = -(40 + (15 if s == 252 else 0))
            else:
                delta = city(s, by)
            ctrl[s] = by
        elif kind == 'ukr':
            nat = args[0]
            for tag, ss in UPRISE.items():
                if tag == 'UNS' and nat:
                    continue
                for i in ss:
                    if own[i] == 'RKU':
                        o.append([i, tag]); own[i] = ctrl[i] = tag
                        delta += city(i, tag)
            out.append('_ukr')
        elif kind == 'ucrush':
            tag, to = args
            for i in owner:
                if own[i] == tag:
                    o.append([i, to]); own[i] = ctrl[i] = to
                    delta += city(i, to)
            out.append(tag)
        elif kind == 'rkufall':
            best = args[0]
            for i in owner:
                if own[i] == 'RKU':
                    to = ctrl[i] if ctrl[i] in UKRT + [S] else best
                    o.append([i, to]); own[i] = ctrl[i] = to
                    delta += city(i, to)
            out.append('RKU')
        elif kind == 'unify':
            leader, joiners = args
            for i in owner:
                if own[i] in joiners:
                    o.append([i, leader]); own[i] = ctrl[i] = leader
            out += list(joiners)
        elif kind == 'rkback':
            tag = args[0]
            for i in owner:
                if own[i] == tag:
                    o.append([i, 'RKU']); own[i] = ctrl[i] = 'RKU'
                    delta += city(i, 'RKU')
            out += [tag, '_rkback']
        elif kind == 'rko':
            for i in RISE_FBR:
                if own[i] == 'RKO':
                    o.append([i, 'FBR']); own[i] = ctrl[i] = 'FBR'; delta += city(i, 'FBR')
            for i in RISE_BLR:
                if own[i] == 'RKO':
                    o.append([i, 'BLR']); own[i] = ctrl[i] = 'BLR'; delta += city(i, 'BLR')
            out.append('_rko')
        elif kind == 'elf':
            if own[811] == 'RKO':
                o.append([811, 'EST']); own[811] = ctrl[811] = 'EST'; delta += city(811, 'EST')
            out.append('_elf')
        elif kind == 'ocrush':
            tag, to = args
            for i in owner:
                if own[i] == tag:
                    o.append([i, to]); own[i] = ctrl[i] = to
                    delta += city(i, to)
            out.append(tag)
        elif kind == 'rkofall':
            est = 'EST' in own.values()
            for i in owner:
                if own[i] != 'RKO':
                    continue
                if ctrl[i] == 'BLR' and i not in BELA:
                    to = 'FBR'                   # Belarus never gets Latgale or other Baltic land
                elif ctrl[i] in RKOT + [S]:
                    to = ctrl[i]
                elif i == 812 and est:
                    to = 'EST'
                elif i in BALT:
                    to = 'FBR'
                elif i in BELA:
                    to = 'BLR'
                else:
                    continue
                o.append([i, to]); own[i] = ctrl[i] = to
                delta += city(i, to)
            for i in owner:
                if own[i] == 'FBR':
                    o.append([i, 'BUN']); own[i] = ctrl[i] = 'BUN'
                elif own[i] == 'EST':
                    o.append([i, 'ESW']); own[i] = ctrl[i] = 'ESW'
            out += ['RKO', '_bun'] + (['_esw'] if est else [])
        elif kind == 'rkoback':
            tag = args[0]
            for i in owner:
                if own[i] == tag:
                    o.append([i, 'RKO']); own[i] = ctrl[i] = 'RKO'
                    delta += city(i, 'RKO')
            out += [tag, '_re_RKO']
        elif kind == 'revwin':
            for i in owner:
                if owner[i] in ('RKM', 'RKK') and own[i] in (S, 'GER'):
                    o.append([i, owner[i]]); own[i] = ctrl[i] = owner[i]
                elif ctrl[i] == 'GER' and own[i] == S:
                    o.append([i, 'GER']); own[i] = 'GER'      # the Reich keeps the rest of what it holds
            out += ['_re_RKM', '_re_RKK', '_revwin', 'SME']
        elif kind == 'cap':
            delta = 20; out.append(args[0])
        elif kind == 'idle':
            delta = -10
        elif kind == 'win':
            for i, ow in owner.items():
                if ow in ('RKM', 'RKK'):
                    o.append([i, 'SME']); own[i] = ctrl[i] = 'SME'
            out += ['RKM', 'RKK']
        elif kind == 'lose':
            if score > -100:
                pass
            for i in owner:
                if own[i] == 'SME' and ctrl[i] != 'SME':
                    o.append([i, ctrl[i]]); own[i] = ctrl[i]       # the Ostschild keeps what it holds
                elif own[i] != 'SME' and ctrl[i] == 'SME':
                    o.append([i, own[i]]); ctrl[i] = own[i]        # and gets back what it lost
            delta = -100 - score
        elif kind == 'gsplit':
            for tag, ss in GCW_SPLIT.items():
                for i in ss:
                    o.append([i, tag]); own[i] = ctrl[i] = tag
        elif kind == 'gcw':
            for i, tag in args:
                c.append([i, tag]); ctrl[i] = tag
        elif kind == 'gann':
            lost, win = args
            for i in owner:
                if own[i] == lost:
                    o.append([i, win]); own[i] = ctrl[i] = win
            out.append(lost)
        elif kind == 'reunify' and any(v in GCW_SPLIT for v in own.values()):
            for i in owner:
                if own[i] in GCW_SPLIT:
                    o.append([i, 'GER']); own[i] = ctrl[i] = 'GER'
        elif kind == 'month':
            delta = -5
        elif kind == 'rk':
            for i in owner:
                if own[i] == 'GER' and owner[i] != 'GER':
                    back = 'RKM' if owner[i] == 'SME' else owner[i]
                    o.append([i, back]); own[i] = ctrl[i] = back
                elif ctrl[i] == 'GER' and own[i] != 'GER':
                    c.append([i, own[i]]); ctrl[i] = own[i]
            out += ['_rk']
        elif kind == 'break':
            tag = args[0]
            for i in BREAK[tag]:
                if own.get(i) == 'SME':
                    o.append([i, tag]); own[i] = ctrl[i] = tag
            if not o:
                text = text.rstrip('.') + " - but its land is no longer the SME's, so it never forms."
        if frozen:
            delta = 0
        score = max(-100, min(170, score + delta))
        steps.append({'d': date, 'k': kind, 'c': c, 'o': o, 'dl': delta, 'sc': score, 't': text, 'out': out})
        if kind in ('lose', 'win'):
            frozen = won = True
    return steps


SCEN = [
    {'id': 'sme', 'name': 'SME victory', 'steps': run(EV_SME, True, True), 'sides': ['SME'] + OST, 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'RKU', 'RKO']},
    {'id': 'ost', 'name': 'The Ostschild does everything right', 'steps': run(EV_OST), 'sides': ['SME'] + OST, 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'RKU', 'RKO']},
    {'id': 'moscow', 'name': 'The battles for Moscow', 'steps': run(EV_MOSCOW), 'sides': ['SME'] + OST, 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'RKU', 'RKO']},
    {'id': 'reich', 'name': 'Holding on until the Reich returns', 'steps': run(EV_REICH), 'sides': ['SME'] + OST + ['GER'], 'late': {'GER': 'reunify'},
     'gsides': ['GOR', 'BOR', 'SPG', 'DWM', 'SSR', 'BMP', 'GAG'], 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'GER', 'RKU', 'RKO']},
    {'id': 'back', 'name': 'The Reich takes back the East', 'steps': run(EV_BACK, True, True), 'sides': ['SME'] + OST + ['GER'], 'late': {'GER': 'reunify'},
     'gsides': ['GOR', 'BOR', 'SPG', 'DWM', 'SSR', 'BMP', 'GAG'], 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'GER', 'RKU', 'RKO']},
]
json.dump({'sides': {'SME': 'SME', 'ost': OST}, 'scenarios': SCEN,
           'countries': {k: {'name': v[0], 'color': v[1]} for k, v in {**BREAK_C, **GCW_C, **UKR_C, **RKO_C}.items()}},
          open(os.path.join(HERE, 'war.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
for sc in SCEN:
    print('==', sc['name'])
    for st in sc['steps']:
        print(st['d'], f"{st['dl']:+4d}", f"{st['sc']:4d}", st['t'][:60])
