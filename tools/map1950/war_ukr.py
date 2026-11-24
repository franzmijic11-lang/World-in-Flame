p = 'war_scenario.py'
t = open(p, encoding='utf-8').read()


def rep(a, b):
    global t
    assert t.count(a) == 1, a[:70]
    t = t.replace(a, b)


# ---------------------------------------------------------------- the scorer
rep("""def run(EV):
    score, held, prewar_lost, steps = 5, set(), set(), []
    ctrl, own = dict(owner), dict(owner)
    for date, kind, args, text in EV:
        delta, c, o, out = 0, [], [], []
        if kind == 'take':
            s, by = args
            c.append([s, by])
            if s in PREWAR:
                if by == S and s in prewar_lost:
                    prewar_lost.discard(s); delta = 40 + (15 if s == 252 else 0)
                elif by != S and s not in prewar_lost:
                    prewar_lost.add(s); delta = -(40 + (15 if s == 252 else 0))
            elif s in CITIES:
                if by == S and s not in held:
                    held.add(s); delta = CITIES[s]
                elif by != S and s in held:
                    held.discard(s); delta = -2 * CITIES[s]
            ctrl[s] = by""", """UKRT = ['UKR', 'UKS', 'UFS', 'UNS']
UPRISE = {'UKR': [193, 225, 259], 'UKS': [227, 200], 'UFS': [197], 'UNS': [199]}
UKR_C = {'UKR': ('Republic of Ukraine', '#e8d34a'), 'UKS': ('Ukrainian Socialist Republic', '#b02222'),
         'UFS': ('Ukrainian National Farmers State', '#96a03c'), 'UNS': ('Ukrainian National State', '#463228')}


def run(EV, stop_at_win=False):
    score, held, ukr_held, prewar_lost, steps = 5, set(), set(), set(), []
    ctrl, own = dict(owner), dict(owner)
    sme_side = lambda by: by == S or by in UKRT

    def city(s, by):
        # The SME's score for a city changing hands. The Ukrainians' gains count like the
        # SME's; a city they lose costs only its value, never double (user, 2026-11-24).
        if s in PREWAR or s not in CITIES:
            return 0
        if sme_side(by):
            if by in UKRT: ukr_held.add(s)
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
        if stop_at_win and score >= 170 and kind not in ('win',):
            steps.append({'d': date, 'k': 'win', 'c': [], 'o': [[i, 'SME'] for i, ow in own.items() if ow in ('RKM', 'RKK')],
                          'dl': 0, 'sc': score, 'out': ['RKM', 'RKK'],
                          't': "The war score reaches +170: the SME has won. It annexes Moskowien and Kaukasien and makes peace with everyone else. What becomes of Ukraine is now for the Ukrainians - and for the Reich, if it ever comes back."})
            break
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
            out += [tag, '_rkback']""")
rep("""        elif kind == 'lose':""", """        elif kind == 'lose':
            if score > -100:
                pass""")


# ---------------------------------------------------------------- the four runs with the Ukrainian front
EXTRA = r'''

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
'''
rep("\nBREAK = {", EXTRA + "\nBREAK = {")
rep("""    {'id': 'sme', 'name': 'SME victory', 'steps': run(EV_SME), 'sides': ['SME'] + OST},""",
    """    {'id': 'sme', 'name': 'SME victory', 'steps': run(EV_SME, True), 'sides': ['SME'] + OST, 'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'RKU']},""")
rep("""    {'id': 'ost', 'name': 'The Ostschild does everything right', 'steps': run(EV_OST), 'sides': ['SME'] + OST},
    {'id': 'moscow', 'name': 'The battles for Moscow', 'steps': run(EV_MOSCOW), 'sides': ['SME'] + OST},""",
    """    {'id': 'ost', 'name': 'The Ostschild does everything right', 'steps': run(EV_OST), 'sides': ['SME'] + OST, 'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'RKU']},
    {'id': 'moscow', 'name': 'The battles for Moscow', 'steps': run(EV_MOSCOW), 'sides': ['SME'] + OST, 'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'RKU']},""")
rep("""'gsides': ['GOR', 'BOR', 'SPG', 'DWM', 'SSR', 'BMP', 'GAG'], 'focus': ['RKM', 'RKK', 'SME', 'GER']},""",
    """'gsides': ['GOR', 'BOR', 'SPG', 'DWM', 'SSR', 'BMP', 'GAG'], 'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'GER', 'RKU']},""")
rep("""{**BREAK_C, **GCW_C}.items()}},""", """{**BREAK_C, **GCW_C, **UKR_C}.items()}},""")
open(p, 'w', encoding='utf-8').write(t)

# ---------------------------------------------------------------- the panel: a row for the Ukrainian rising
p = 'patch_war.py'
t = open(p, encoding='utf-8').read()
a = '      <div class="warsides" id="warGerman"></div>'
assert t.count(a) == 1
t = t.replace(a, a + '\n      <div class="warsides" id="warUkraine"></div>')
a = '  const log = $("warLog");'
assert t.count(a) == 1
t = t.replace(a, '''  const us = scen.usides || [];
  const urose = warOut.has("_ukr");
  $("warUkraine").hidden = !us.length || !urose;
  $("warUkraine").innerHTML = us.length ? '<span class="hint" style="width:100%">The Ukrainian rising (fights for the SME\\'s score)</span>' + us.map((t) => `<span class="warside${warOut.has(t) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t))}${warOut.has(t) ? " \\u2014 gone" : ""}</span>`).join("") : "";
''' + a)
open(p, 'w', encoding='utf-8').write(t)
print('ok')
