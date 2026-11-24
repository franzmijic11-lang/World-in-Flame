"""Adds the Ostland collapse (tools/gen_rko.py) to the four war runs and a fifth run, 'The Reich
takes back the East'. Patches war_scenario.py and patch_war.py in place (run once, after war_ukr.py)."""
p = 'war_scenario.py'
t = open(p, encoding='utf-8').read()


def rep(a, b):
    global t
    assert t.count(a) == 1, a[:70]
    t = t.replace(a, b)


# ---------------------------------------------------------------- tags
rep("""def run(EV, stop_at_win=False):
    score, held, ukr_held, prewar_lost, steps = 5, set(), set(), set(), []
    ctrl, own = dict(owner), dict(owner)
    sme_side = lambda by: by == S or by in UKRT
""", """RKOT = ['FBR', 'BUN', 'BLR', 'EST', 'ESW']
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
""")
rep("""            if by in UKRT: ukr_held.add(s)""", """            if by in PART: ukr_held.add(s)""")
rep("""        if stop_at_win and score >= 170 and kind not in ('win',):
            steps.append({'d': date, 'k': 'win', 'c': [], 'o': [[i, 'SME'] for i, ow in own.items() if ow in ('RKM', 'RKK')],
                          'dl': 0, 'sc': score, 'out': ['RKM', 'RKK'],
                          't': "The war score reaches +170: the SME has won. It annexes Moskowien and Kaukasien and makes peace with everyone else. What becomes of Ukraine is now for the Ukrainians - and for the Reich, if it ever comes back."})
            break
""", """        if stop_at_win and score >= 170 and not won and kind != 'win':
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
""")
rep("""        elif kind == 'cap':
            delta = 20; out.append(args[0])""", """        elif kind == 'rko':
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
                if ctrl[i] in RKOT + [S]:
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
                    c.append([i, own[i]]); ctrl[i] = own[i]
            out += ['_re_RKM', '_re_RKK', '_revwin']
        elif kind == 'cap':
            delta = 20; out.append(args[0])""")
rep("""        score = max(-100, min(170, score + delta))
        steps.append({'d': date, 'k': kind, 'c': c, 'o': o, 'dl': delta, 'sc': score, 't': text, 'out': out})""",
    """        if frozen:
            delta = 0
        score = max(-100, min(170, score + delta))
        steps.append({'d': date, 'k': kind, 'c': c, 'o': o, 'dl': delta, 'sc': score, 't': text, 'out': out})
        if kind in ('lose', 'win'):
            frozen = won = True""")

# ---------------------------------------------------------------- the events
EXTRA = r'''

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
    ('1955-03-16', 'revwin', (), "The SME makes peace. Reichskommissariat Moskowien and Reichskommissariat Kaukasien are re-established, and the East is the Reich's once more."),
]
EV_BACK = sorted(EV_BACK, key=lambda e: e[0])
'''
rep("\nBREAK = {", EXTRA + "\nBREAK = {")
rep("""    {'id': 'sme', 'name': 'SME victory', 'steps': run(EV_SME, True), 'sides': ['SME'] + OST, 'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'RKU']},""",
    """    {'id': 'sme', 'name': 'SME victory', 'steps': run(EV_SME, True, True), 'sides': ['SME'] + OST, 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'RKU', 'RKO']},""")
rep("""'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'RKU']},
    {'id': 'moscow'""", """'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'RKU', 'RKO']},
    {'id': 'moscow'""")
rep("""{'id': 'moscow', 'name': 'The battles for Moscow', 'steps': run(EV_MOSCOW), 'sides': ['SME'] + OST, 'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'RKU']},""",
    """{'id': 'moscow', 'name': 'The battles for Moscow', 'steps': run(EV_MOSCOW), 'sides': ['SME'] + OST, 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'RKU', 'RKO']},""")
rep("""'usides': UKRT, 'focus': ['RKM', 'RKK', 'SME', 'GER', 'RKU']},
]""", """'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'GER', 'RKU', 'RKO']},
    {'id': 'back', 'name': 'The Reich takes back the East', 'steps': run(EV_BACK, True, True), 'sides': ['SME'] + OST + ['GER'], 'late': {'GER': 'reunify'},
     'gsides': ['GOR', 'BOR', 'SPG', 'DWM', 'SSR', 'BMP', 'GAG'], 'usides': UKRT, 'osides': RKOT, 'focus': ['RKM', 'RKK', 'SME', 'GER', 'RKU', 'RKO']},
]""")
rep("""{**BREAK_C, **GCW_C, **UKR_C}.items()}},""", """{**BREAK_C, **GCW_C, **UKR_C, **RKO_C}.items()}},""")
open(p, 'w', encoding='utf-8').write(t)

# ---------------------------------------------------------------- the panel
p = 'patch_war.py'
t = open(p, encoding='utf-8').read()
a = '      <div class="warsides" id="warUkraine"></div>'
assert t.count(a) == 1
t = t.replace(a, a + '\n      <div class="warsides" id="warOstland"></div>')
a = '  const log = $("warLog");'
assert t.count(a) == 1
t = t.replace(a, '''  const os = scen.osides || [];
  const orose = warOut.has("_rko");
  const present = new Set(Object.values(warOwn));
  const oshow = os.filter((t) => present.has(t) || warOut.has(t));
  const onote = (t) => t === "FBR" && warOut.has("_bun") ? " \\u2014 now the Baltic Union" : t === "EST" && warOut.has("_esw") ? " \\u2014 now a Swedish supervised state" : warOut.has(t) ? " \\u2014 gone" : "";
  $("warOstland").hidden = !os.length || !orose;
  $("warOstland").innerHTML = os.length ? '<span class="hint" style="width:100%">The Ostland rising (fights for the SME\\'s score)</span>' + oshow.map((t) => `<span class="warside${warOut.has(t) || (t === "FBR" && warOut.has("_bun")) || (t === "EST" && warOut.has("_esw")) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t))}${onote(t)}</span>`).join("") : "";
''' + a)
# re-established Reichskommissariate are not struck out
a = """  $("warSides").innerHTML = sides.map((t) => `<span class="warside${warOut.has(t) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t).replace(/^Reichskommissariat /, "RK ").replace(/ \\(.*\\)$/, ""))}${warOut.has(t) ? (t === "SME" ? " — collapsing" : " — capitulated") : (rk && t !== "SME" && t !== "GER" ? " — a Reichskommissariat again" : (late[t] ? " — at war" : ""))}</span>`).join("");"""
assert t.count(a) == 1, 'sides line'
t = t.replace(a, """  const re = (t) => warOut.has("_re_" + t) || (t === "RKU" && warOut.has("_rkback"));
  const gone = (t) => warOut.has(t) && !re(t);
  const sideNote = (t) => re(t) ? " — re-established" : gone(t) ? (t === "SME" ? " — collapsing" : (t === "RKM" || t === "RKK") && warOut.has("_won") ? " — annexed by the SME" : " — capitulated") : (rk && t !== "SME" && t !== "GER" ? " — a Reichskommissariat again" : (late[t] ? " — at war" : ""));
  $("warSides").innerHTML = sides.map((t) => `<span class="warside${gone(t) ? " out" : ""}"><i style="background:${color50(t)}"></i>${esc50(name50(t).replace(/^Reichskommissariat /, "RK ").replace(/ \\(.*\\)$/, ""))}${sideNote(t)}</span>`).join("");""")
t = t.replace('if (st.k === "lose") warOut.add("SME");', 'if (st.k === "lose") warOut.add("SME");\n    if (st.k === "win") warOut.add("_won");')
t = t.replace("<p class=\"hint\">Two imagined runs of the war from March 1952", "<p class=\"hint\">Imagined runs of the war from March 1952")
open(p, 'w', encoding='utf-8').write(t)
print('ok')
