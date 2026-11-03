import json, time, os

OUTDIR = os.path.dirname(os.path.abspath(__file__))


def build(prefix, name, tag, tree_id, rows, out, target=1825):
    keys = {r[0] for r in rows}
    ids = {r[0]: f'{prefix}{i:03d}' for i, r in enumerate(rows)}
    focuses = []
    for (key, nm, x, y, days, br, desc, pre, any_, mx, auto) in rows:
        for k in list(pre) + list(mx):
            assert k in keys, (key, k)
        focuses.append(dict(id=ids[key], fid=f'wif_{tag.lower()}_{key}', name=nm, desc=desc, days=days,
                            x=x, y=y, branch=br, pre=[ids[k] for k in pre], after=[], any=any_,
                            mx=[ids[k] for k in mx], auto=auto))
    cells = [(f['x'], f['y']) for f in focuses]
    assert len(cells) == len(set(cells)), 'overlap'
    for f in focuses:
        for o in f['mx']:
            assert f['id'] in next(g for g in focuses if g['id'] == o)['mx'], 'mx not mutual'
    player = sum(r[4] for r in rows if not r[10])
    pairs = {tuple(sorted((r[0], m))) for r in rows for m in r[9]}
    player -= sum(next(r[4] for r in rows if r[0] == a) for a, b in pairs)
    print(name, len(rows), 'focuses, player days', player, round(player / 365, 2), 'years')
    doc = dict(name=name, tag=tag, treeId=tree_id, target=target, focuses=focuses,
               updatedAt=int(time.time() * 1000))
    json.dump(doc, open(os.path.join(OUTDIR, out), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)


def F(key, nm, x, y, days, br, desc, pre=(), any_=False, mx=(), auto=False):
    return (key, nm, x, y, days, br, desc, list(pre), any_, list(mx), auto)


# =====================================================================
# Popov - the Central Siberian Republic (CSR), Tomsk
# =====================================================================
CSR = [
    # --- the Duma (political, x 5-7)
    F('tomsk_declaration', 'The Tomsk Declaration', 6, 0, 35, 'political',
      "Siberia will be ruled neither from Moscow nor from Irkutsk. Marshal Popov has promised a republic, and now he has to build one out of an army, a railway and a few frozen cities.\n\n"
      "Starting spirits (negative): Anarchist Rebels, Heavy Church Influence, Food Shortages, A Republic of Soldiers.\n\nEffect: +5% stability."),
    F('provisional', 'A Provisional Government', 6, 1, 70, 'political',
      "Ministers appointed by the Marshal, to govern until the people can choose their own.\n\nEffect: +50 political power.", ['tomsk_declaration']),
    F('assembly', 'Call a Constituent Assembly', 6, 2, 70, 'political',
      "Every district, every town soviet, every regiment sends delegates to Tomsk to decide what Siberia is.\n\nEffect: +5% stability.", ['provisional']),
    F('parties', 'Legalise the Parties', 5, 3, 49, 'political',
      "Kadets, Socialist Revolutionaries, Mensheviks, regionalists - all of them banned for twenty years, all of them back.\n\nEffect: democratic popularity +10%.", ['assembly']),
    F('press', 'A Free Press in Tomsk', 7, 3, 49, 'political',
      "Newspapers nobody censors, saying things the Marshal does not always like.\n\nEffect: +5% stability, -5% war support.", ['assembly']),
    F('campaign', 'The Duma Campaign', 6, 4, 70, 'political',
      "Posters on every station wall from Omsk to Krasnoyarsk, and soldiers guarding the polling stations from the anarchists.\n\nEffect: +25 political power.", ['parties', 'press']),
    F('election', 'Elections to the Siberian Duma', 6, 5, 105, 'political',
      "The first free vote east of the Urals since 1917.\n\nEffect: holds the election; elections allowed from now on. +10% stability.", ['campaign']),
    F('coalition', 'A Coalition of the Centre', 5, 6, 70, 'political',
      "The parties govern together, and the Marshal stays out of the chamber.\n\nEffect: +10% stability, -5% war support. Removes A Republic of Soldiers.", ['election'], mx=['marshals_bloc']),
    F('marshals_bloc', "The Marshal's Bloc", 7, 6, 70, 'political',
      "Popov's own list wins, and the army's men take the ministries.\n\nEffect: +10% war support. A Republic of Soldiers is weakened rather than removed.", ['election'], mx=['coalition']),
    F('duma_seated', 'The Duma Is Seated', 6, 7, 49, 'political',
      "Four hundred deputies in the old merchants' club in Tomsk. It is cold, it is crowded, and it is a parliament.\n\nEffect: +0.1 daily political power.", ['coalition', 'marshals_bloc'], any_=True),
    F('constitution', 'The Tomsk Constitution', 6, 8, 70, 'political',
      "A republic on paper, signed by the Duma and by the Marshal.\n\nEffect: +10% stability.", ['duma_seated']),

    # --- the troubles (inner, x 0-3): nothing the republic can do about them.
    # These complete themselves and only ever make things worse.
    F('banners_spread', 'The Black Banners Spread', 1, 2, 140, 'inner',
      "He does nothing; it happens anyway. The anarchist bands take another district of the taiga, and the republic has neither the men nor the authority to take it back.\n\nEffect: Anarchist Rebels grow stronger.", ['tomsk_declaration'], auto=True),
    F('rail_sabotage', 'Sabotage on the Ob Line', 1, 4, 210, 'inner',
      "It happens anyway. Bridges burn, trains stop, and the Black Banners print their own newspaper.\n\nEffect: Anarchist Rebels at their worst; -supply in the anarchist districts.", ['banners_spread'], auto=True),
    F('sermons', 'Sermons Against the Duma', 3, 2, 140, 'inner',
      "It happens anyway. With the commissars gone, the Church came back faster than anyone expected, and from every pulpit it tells the villages a parliament is godless.\n\nEffect: Heavy Church Influence grows stronger.", ['tomsk_declaration'], auto=True),
    F('blessing', 'The Church Blesses the Marshal', 3, 4, 210, 'inner',
      "It happens anyway. The Metropolitan of Novosibirsk prays for Marshal Popov by name - and for the Duma not at all.\n\nEffect: Heavy Church Influence at its worst; democratic popularity -5%.", ['sermons'], auto=True),

    # --- more of the republic (player time freed by the troubles)
    F('refugees', 'Refugees from the West', 8, 2, 84, 'political',
      "Hundreds of thousands fled across the Urals ahead of the Germans and the SME. They need bread, roofs and papers.\n\nEffect: +20,000 manpower, -5% stability.", ['provisional']),
    F('zemstvo', 'Zemstvo Councils', 4, 4, 70, 'political',
      "District councils, elected, to run the roads, schools and grain stores.\n\nEffect: +5% stability.", ['assembly']),
    F('land_question', 'The Land Question', 8, 6, 70, 'political',
      "The kolkhozes are breaking up on their own. The Duma must decide who owns the land.\n\nEffect: +5% stability, democratic popularity +5%.", ['election']),
    F('siberian_ruble', 'The Siberian Ruble', 12, 4, 70, 'economy',
      "Soviet rubles are worthless east of the Urals. Tomsk prints its own.\n\nEffect: +5% consumer goods relief.", ['rationing']),
    F('army_oath', 'The Army Swears to the Duma', 4, 7, 70, 'military',
      "Every regiment takes the oath to the republic, not to the Marshal.\n\nEffect: +5% stability, +5% war support.", ['duma_seated']),

    # --- food (economy, x 9-11)
    F('grain_census', 'A Grain Census', 10, 1, 49, 'economy',
      "How much grain is in the elevators, and how many mouths there are to feed until the harvest.\n\nEffect: +25 political power.", ['tomsk_declaration'], auto=True),
    F('rationing', 'Food Rationing', 10, 2, 105, 'economy',
      "Ration cards for every city - bread first, then sugar, then everything.\n\nEffect: Food Shortages weakened; -5% stability.", ['grain_census']),
    F('requisition', 'Requisition from the Altai', 9, 3, 49, 'economy',
      "The army collects the grain from the farms, as the Bolsheviks did.\n\nEffect: Food Shortages weakened; -5% stability.", ['rationing'], mx=['free_markets']),
    F('free_markets', 'Free Grain Markets', 11, 3, 70, 'economy',
      "Let the peasants sell their grain at whatever price it fetches.\n\nEffect: Food Shortages weakened; -10% consumer goods slowly.", ['rationing'], mx=['requisition']),
    F('kuzbass_fed', 'Feed the Kuzbass Miners First', 10, 4, 70, 'economy',
      "No coal without miners, no miners without bread.\n\nEffect: +5% factory output.", ['requisition', 'free_markets'], any_=True),
    F('harvest', 'The Harvest of the Ob', 10, 5, 105, 'economy',
      "The first good harvest since the war.\n\nEffect: removes Food Shortages.", ['kuzbass_fed']),

    # --- army and industry (x 13-15)
    F('popovs_army', 'The Army Popov Brought', 14, 1, 49, 'military',
      "A third of the SME's eastern army followed him to Tomsk. It is the only reason the republic exists.\n\nEffect: +army experience.", ['tomsk_declaration']),
    F('kuzbass', 'Kuzbass Coal and Steel', 13, 2, 70, 'industry',
      "The Kuznetsk basin is the heart of whatever industry Siberia has.\n\nEffect: +1 civilian factory, +steel.", ['popovs_army']),
    F('novosibirsk', 'The Novosibirsk Works', 15, 2, 70, 'industry',
      "The factories evacuated east in 1941 are still here.\n\nEffect: +1 military factory.", ['popovs_army']),
    F('rifles', 'Siberian Rifle Divisions', 14, 3, 70, 'military',
      "The divisions that saved Moscow in 1941 came from here. They can do it again.\n\nEffect: +5% division organisation.", ['kuzbass', 'novosibirsk'], any_=True),
    F('yenisei', 'Hold the Yenisei', 14, 4, 70, 'military',
      "The river is the border with Stalin. Fort the crossings.\n\nEffect: forts along the eastern border.", ['rifles']),
    F('plans_east', 'Plans for the East', 14, 5, 70, 'military',
      "The staff draws the arrows towards Irkutsk.\n\nEffect: +5% attack against the FES.", ['yenisei']),

    # --- the end
    F('march_east', 'March East', 8, 9, 105, 'military',
      "Stalin is still alive in Irkutsk, and as long as he is, Siberia is not free.\n\nEffect: declares war on the Far Eastern Union. About half a year in, the collapse mechanic (to be added) decides it.",
      ['constitution', 'army_oath', 'harvest', 'plans_east']),
]

# =====================================================================
# Stalin - the Far Eastern Union (FES), Irkutsk
# =====================================================================
FES = [
    # --- clinging to power (political, x 5-7)
    F('irkutsk', 'Irkutsk, Not Moscow', 6, 0, 35, 'political',
      "The war was lost, Moscow was lost, and the Emergency Government hunted him across the Urals. He is still the Vozhd.\n\n"
      "Starting spirits (negative): The Vozhd's Paranoia, Food Shortages, An Army That Lost, Siberian White Army Remnant Resistance.\n\nEffect: +5% stability."),

    # --- the Whites (x 17): nothing Stalin can do about them. These complete
    # themselves and only ever make Siberian White Army Remnant Resistance worse.
    F('whites_taiga', 'The Whites in the Taiga', 17, 1, 140, 'inner',
      "It happens anyway. Kolchak's men never all went to Harbin. Their sons kept the rifles, and with the Red Army broken they have come out of the forest.\n\nEffect: Siberian White Army Remnant Resistance grows stronger.", ['irkutsk'], auto=True),
    F('amur_ambush', 'Ambushes on the Amur Road', 17, 3, 210, 'inner',
      "It happens anyway. Convoys vanish between Chita and Blagoveshchensk, and the villages say they saw nothing.\n\nEffect: Siberian White Army Remnant Resistance at its worst; -supply in the eastern states.", ['whites_taiga'], auto=True),
    F('atamans_banner', "The Ataman's Banner Raised Again", 17, 5, 210, 'inner',
      "It happens anyway. Semyonov's old banner flies over a Transbaikal stanitsa, and Cossacks ride under it.\n\nEffect: Siberian White Army Remnant Resistance grows; -5% stability.", ['amur_ambush'], auto=True),
    F('vozhd', 'The Vozhd Still Rules', 6, 1, 70, 'political',
      "Every order still goes out under his name, as it did from the Kremlin.\n\nEffect: +50 political power.", ['irkutsk']),
    F('portraits', 'Portraits in Every Office', 5, 2, 70, 'political',
      "His face on every wall from Chita to Magadan.\n\nEffect: communist popularity +10%.", ['vozhd']),
    F('pravda_east', 'Pravda of the East', 7, 2, 70, 'political',
      "The Irkutsk Pravda tells the people that the war was not lost - it was betrayed.\n\nEffect: +5% war support.", ['vozhd']),
    F('cult', 'The Cult Reborn', 6, 3, 70, 'political',
      "Songs, statues, a new short course of party history.\n\nEffect: +10% stability.", ['portraits', 'pravda_east']),
    F('betrayed', 'Moscow Was Lost by Traitors', 6, 4, 70, 'political',
      "Not by him. Never by him.\n\nEffect: +10% war support, -5% stability.", ['cult']),
    F('loyal_marshals', 'The Marshals Who Came East', 6, 5, 70, 'political',
      "Every commander here was on the train east with him. They are all the high command he has left.\n\nEffect: +army experience, new generals.", ['betrayed']),
    F('union_lives', 'The Union Lives in Irkutsk', 6, 6, 140, 'political',
      "The lawful government of the USSR, in exile in its own country.\n\nEffect: claims on Popov's republic.", ['loyal_marshals']),

    # --- paranoia (inner, x 0-3). There is nobody left to purge: everyone in
    # Irkutsk chose him over Moscow. The fear turns inward and has nowhere to go.
    F('the_few', 'The Few Who Came East', 2, 1, 49, 'inner',
      "Every man around him chose the Vozhd over Moscow and followed him across Siberia. That ought to be enough. It is not.\n\nEffect: The Vozhd's Paranoia grows; +50 political power.", ['irkutsk']),
    F('sleeps_badly', 'The Vozhd Sleeps Badly', 0, 2, 70, 'inner',
      "He does this himself. Someone warned him in Moscow, so someone could betray him here.\n\nEffect: The Vozhd's Paranoia grows.", ['the_few'], auto=True),
    F('tasters', 'Tasters at Every Meal', 2, 2, 49, 'inner',
      "Nothing reaches his table that someone else has not eaten first.\n\nEffect: -5% stability.", ['the_few']),
    F('by_telephone', 'Rule by Telephone', 1, 3, 70, 'inner',
      "He stops leaving the house. Orders come down the line at three in the morning.\n\nEffect: The Vozhd's Paranoia eases a little; -10% political power gain.", ['tasters'], mx=['show_himself']),
    F('show_himself', 'Show Himself to the Troops', 3, 3, 49, 'inner',
      "A review on the parade ground, every rifle unloaded first.\n\nEffect: +10% war support; The Vozhd's Paranoia grows.", ['tasters'], mx=['by_telephone']),
    F('papers', 'Nobody Enters Without Papers', 2, 4, 70, 'inner',
      "Passes, countersigned passes, and guards who check each other's.\n\nEffect: -5% stability, +5% resistance to enemy spies.", ['by_telephone', 'show_himself'], any_=True),
    F('doctors', 'Doctors Under Suspicion', 0, 4, 140, 'inner',
      "He does this himself. Even the men who take his pulse might be poisoners.\n\nEffect: The Vozhd's Paranoia grows; -5% research speed.", ['sleeps_badly'], auto=True),
    F('vozhd_alone', 'The Vozhd Alone', 2, 5, 140, 'inner',
      "Loyal men all around him, and he trusts none of them - but there is nobody to shoot, so the fear simply stays.\n\nEffect: The Vozhd's Paranoia becomes permanent at its height; +0.1 daily political power.", ['papers']),
    F('shadows', 'Shadows in the Corridor', 0, 6, 210, 'inner',
      "He does this himself. He hears footsteps where there are none.\n\nEffect: The Vozhd's Paranoia grows.", ['doctors'], auto=True),

    # --- food (economy, x 9-11)
    F('hungry_winter', 'The Hungry Winter', 10, 1, 70, 'economy',
      "He does this himself. The far east never fed itself; the grain came from the west, and the west is gone.\n\nEffect: Food Shortages worsen.", ['irkutsk'], auto=True),
    F('kolkhoz', 'Kolkhoz Quotas', 10, 2, 70, 'economy',
      "Every collective farm east of Baikal gets a number it has to meet.\n\nEffect: Food Shortages weakened.", ['irkutsk']),
    F('raise_quotas', 'Raise the Quotas', 9, 3, 49, 'economy',
      "If the farms cannot meet the quota, the quota is not high enough.\n\nEffect: Food Shortages weakened; -5% stability.", ['kolkhoz'], mx=['private_plots']),
    F('private_plots', 'Allow Private Plots', 11, 3, 70, 'economy',
      "A heresy, but it feeds people.\n\nEffect: Food Shortages weakened; communist popularity -5%.", ['kolkhoz'], mx=['raise_quotas']),
    F('okhotsk_fish', 'Fish from the Sea of Okhotsk', 10, 4, 70, 'economy',
      "The fishing fleet at Magadan and Nikolayevsk feeds the cities.\n\nEffect: Food Shortages weakened.", ['raise_quotas', 'private_plots'], any_=True),
    F('buryat_grain', 'Grain from Buryatia', 10, 5, 105, 'economy',
      "The steppe south of Baikal is the only farmland worth the name.\n\nEffect: removes Food Shortages.", ['okhotsk_fish']),
    F('manchurian_rice', 'Rice Through Manchuria', 11, 6, 70, 'diplomacy',
      "Bought from the Japanese, quietly.\n\nEffect: +opinion with Japan; +consumer goods relief.", ['okhotsk_fish']),

    # --- army and industry (x 13-15)
    F('forty_percent', 'Forty Percent of the Red Army', 14, 1, 49, 'military',
      "The divisions that followed him east are the largest army in Asia that is not Japanese.\n\nEffect: +army experience.", ['irkutsk']),
    F('fronts', 'Re-form the Fronts', 13, 2, 70, 'military',
      "Transbaikal Front, Far Eastern Front - the old names, the old staffs.\n\nEffect: +5% division organisation.", ['forty_percent']),
    F('trans_siberian', 'Guard the Trans-Siberian', 15, 2, 70, 'military',
      "One railway holds the whole country together.\n\nEffect: +infrastructure along the line.", ['forty_percent']),
    F('amur_works', 'The Amur Works', 14, 3, 70, 'industry',
      "Komsomolsk and Khabarovsk build what Moscow used to send.\n\nEffect: +1 military factory.", ['fronts', 'trans_siberian'], any_=True),
    F('ulan_ude_guns', 'Guns from Ulan-Ude', 14, 4, 70, 'military',
      "The locomotive works can build artillery too.\n\nEffect: artillery added to the stockpile.", ['amur_works']),
    F('plan_west', 'Plan West', 14, 5, 70, 'military',
      "The staff draws the arrows towards Tomsk.\n\nEffect: +5% attack against the CSR.", ['ulan_ude_guns']),

    # --- the end
    F('hang_popov', 'Hang the Traitor Popov', 8, 8, 105, 'military',
      "Popov took the army he was given to hunt the Vozhd and made himself a president with it. He will answer for it.\n\nEffect: declares war on the Central Siberian Republic. About half a year in, the collapse mechanic (to be added) decides it.",
      ['union_lives', 'vozhd_alone', 'buryat_grain', 'plan_west']),
]

# =====================================================================
# Yagoda - the West Siberian Marxist Republic (WSM), Tyumen
# About six and a half years, then it collapses (mechanic to be added by the
# user). Holds Tyumen, Chelyabinsk, Sverdlovsk and Tobolsk.
# =====================================================================
WSM = [
    # --- the grip (political, x 6-8)
    F('commissar', 'The Commissar of the Urals', 7, 0, 35, 'political',
      "Genrikh Yagoda ran the NKVD once, and Moscow took it from him. Now Moscow has fallen, and the Urals answer to him.\n\n"
      "Starting spirits (negative): The Organs Rule, Fear of the Commissar, Cut Off from the Union.\n\nEffect: +5% stability."),
    F('proclaim', 'Proclaim the Marxist Republic', 7, 1, 49, 'political',
      "A republic of workers and soldiers, run by the men who used to arrest them.\n\nEffect: +50 political power.", ['commissar']),
    F('sverdlovsk_soviet', 'Dissolve the Sverdlovsk Soviet', 6, 2, 49, 'political',
      "The city soviet thought it could choose its own chairman.\n\nEffect: -5% stability, +5% war support.", ['proclaim']),
    F('party_answers', 'The Party Answers to the Organs', 8, 2, 49, 'political',
      "Every party committee gets an NKVD officer, and he signs the minutes.\n\nEffect: +0.05 daily political power.", ['proclaim']),
    F('through_party', 'Rule Through the Party', 6, 3, 49, 'political',
      "Keep the forms of Soviet power, and fill them with his men.\n\nEffect: communist popularity +10%, +5% stability.", ['sverdlovsk_soviet', 'party_answers'], mx=['through_organs']),
    F('through_organs', 'Rule Through the Organs', 8, 3, 49, 'political',
      "Do away with the pretence. The Commissariat is the government.\n\nEffect: The Organs Rule strengthened; +10% political power gain.", ['sverdlovsk_soviet', 'party_answers'], mx=['through_party']),
    F('order_state', 'The Order State', 7, 4, 105, 'political',
      "Everything permitted is written down. Everything not written down is forbidden.\n\nEffect: +10% stability, -5% war support.", ['through_party', 'through_organs'], any_=True),
    F('registered', 'Every Citizen Registered', 6, 5, 49, 'political',
      "A card for every person in the republic: name, work, address, reliability.\n\nEffect: +5% stability, +manpower.", ['order_state']),
    F('passports', 'Internal Passports', 8, 5, 49, 'political',
      "No travel between towns without a stamp from the organs.\n\nEffect: -5% stability, +resistance to enemy spies.", ['order_state']),
    F('curfew', 'The Long Curfew', 7, 6, 49, 'political',
      "Off the streets at nine. Lights out at ten.\n\nEffect: +5% stability, -5% factory output.", ['registered', 'passports']),
    F('one_voice', 'One Voice in Tyumen', 7, 7, 49, 'political',
      "One newspaper, one radio station, one chairman.\n\nEffect: +10% war support.", ['curfew']),
    F('portraits', 'Portraits of Genrikh Yagoda', 6, 8, 49, 'political',
      "A small man in a commissar's tunic, on every wall in the Urals.\n\nEffect: +5% stability.", ['one_voice']),
    F('no_successor', 'No Successor Named', 8, 8, 49, 'political',
      "Anyone who might replace him is watched more closely than anyone else.\n\nEffect: +0.05 daily political power, -5% stability.", ['one_voice']),
    F('grip_tightens', 'The Grip Tightens', 7, 9, 105, 'political',
      "Every lever in the republic now runs through one office in Tyumen.\n\nEffect: +10% stability, The Organs Rule at its strongest.", ['portraits', 'no_successor']),
    F('absolute_order', 'Absolute Order', 7, 10, 210, 'political',
      "Nothing moves in the Urals that the organs have not allowed. It is the most orderly state in Russia, and it cannot last.\n\nEffect: the end of the tree. The collapse mechanic (to be added) takes it from here.",
      ['grip_tightens', 'yagodas_guard', 'kyshtym', 'commissariat_plan']),

    # --- the secret police (inner, x 1-4)
    F('rebuild_organs', 'Rebuild the Organs', 3, 1, 49, 'inner',
      "The NKVD officers who came over with him become the core of a new Commissariat.\n\nEffect: +50 political power.", ['commissar']),
    F('informers', 'Informers in Every Block', 2, 2, 49, 'inner',
      "Every apartment block has a man who writes reports.\n\nEffect: +5% stability, -5% war support.", ['rebuild_organs']),
    F('special_depts', 'The Special Departments', 4, 2, 49, 'inner',
      "An NKVD officer in every regiment, answering only to Tyumen.\n\nEffect: -5% division organisation, no coup from the army.", ['rebuild_organs']),
    F('camps', 'Camps of the Urals', 2, 3, 49, 'inner',
      "The old Gulag camps around Sverdlovsk fill up again.\n\nEffect: +manpower for labour, -5% stability.", ['informers']),
    F('files', 'A File on Everyone', 4, 3, 49, 'inner',
      "Cabinets of index cards in the basement of the Tyumen Commissariat.\n\nEffect: +intelligence.", ['special_depts']),
    F('open_terror', 'Open Terror', 2, 4, 49, 'inner',
      "Arrests at night, trials by morning, and everyone knows.\n\nEffect: Fear of the Commissar grows; +10% stability for a year, then -10%.", ['camps', 'files'], mx=['quiet_watch']),
    F('quiet_watch', 'Silent Surveillance', 4, 4, 49, 'inner',
      "Nobody is arrested. Everybody is watched.\n\nEffect: Fear of the Commissar eases; -0.05 daily political power.", ['camps', 'files'], mx=['open_terror']),
    F('watchers', 'Who Watches the Watchers', 3, 5, 105, 'inner',
      "A second commissariat to watch the first.\n\nEffect: +5% stability.", ['open_terror', 'quiet_watch'], any_=True),
    F('yagodas_guard', "Yagoda's Own Guard", 3, 6, 49, 'inner',
      "One regiment that answers to him personally, quartered next to his office.\n\nEffect: a guard division.", ['watchers']),
    F('whispers', 'Whispers in the Party', 0, 3, 140, 'inner',
      "It happens anyway. Party men meet in kitchens and talk about who comes after Yagoda.\n\nEffect: -5% stability.", ['rebuild_organs'], auto=True),
    F('officers_resent', 'The Officers Resent the Organs', 0, 6, 210, 'inner',
      "It happens anyway. Every colonel with a commissar at his elbow is a colonel waiting for his moment.\n\nEffect: -5% stability, -5% war support.", ['whispers'], auto=True),
    F('cracks', 'Cracks in the Order', 0, 9, 280, 'inner',
      "It happens anyway. The more tightly he holds the Urals, the more of it slips through his fingers.\n\nEffect: -10% stability.", ['officers_resent'], auto=True),

    # --- the Chelyabinsk Institute (project, x 10-12)
    F('seize_institute', 'Seize the Chelyabinsk Institute', 11, 1, 49, 'project',
      "The Institute for All Research is the greatest prize in the Urals. NKVD troops take the building, the laboratories and every scientist in them.\n\nEffect: the Institute's research bonus is secured; +5% research speed.", ['commissar']),
    F('under_guard', 'Scientists Under Guard', 10, 2, 49, 'project',
      "They work, they eat and they sleep inside the wire.\n\nEffect: +5% research speed, -5% stability.", ['seize_institute']),
    F('sharashka', 'The Urals Sharashka', 12, 2, 49, 'project',
      "A prison design bureau, as the NKVD ran in the 1930s: arrested engineers working for their freedom.\n\nEffect: tech bonus for one industry and one weapons technology.", ['seize_institute']),
    F('weapons_for_organs', 'Weapons for the Organs', 10, 3, 49, 'project',
      "The Institute designs what the Commissariat needs: rifles, radios, armoured cars.\n\nEffect: tech bonuses for infantry weapons and support equipment.", ['under_guard', 'sharashka'], mx=['machines']),
    F('machines', 'Machines for the Factories', 12, 3, 49, 'project',
      "The Institute designs what Uralmash needs.\n\nEffect: tech bonuses for industry.", ['under_guard', 'sharashka'], mx=['weapons_for_organs']),
    F('kyshtym', 'The Kyshtym Project', 11, 4, 140, 'project',
      "A closed town by Lake Kyzyltash, south of Sverdlovsk, where the Institute's physicists work on something nobody may name.\n\nEffect: +nuclear research.", ['weapons_for_organs', 'machines'], any_=True),
    F('prisoners_invent', 'Prisoners Who Invent', 11, 5, 49, 'project',
      "The sharashka's best engineers are promised their freedom. None of them get it.\n\nEffect: +5% research speed.", ['kyshtym']),

    # --- industry and food (industry / economy, x 14-16)
    F('uralmash', 'Uralmash Under the Organs', 15, 1, 49, 'industry',
      "The Ural heavy machinery works gets a new director from the Commissariat.\n\nEffect: +1 civilian factory.", ['commissar']),
    F('tankograd', 'Tankograd', 14, 2, 49, 'industry',
      "The Chelyabinsk tractor works built tanks for the whole war. It can build them for the republic.\n\nEffect: +1 military factory.", ['uralmash']),
    F('prison_labour', 'Prisoners for the Mines', 16, 2, 49, 'industry',
      "The camps supply the mines with labour that cannot leave.\n\nEffect: +steel, -5% stability.", ['uralmash']),
    F('tobolsk_grain', 'Grain from Tobolsk', 15, 3, 49, 'economy',
      "The only farmland the republic holds is along the Tobol and the Irtysh.\n\nEffect: food shortages ease.", ['tankograd', 'prison_labour']),
    F('sverdlovsk_arms', 'The Sverdlovsk Arms Works', 14, 4, 49, 'industry',
      "Rifles and machine guns for the NKVD troops.\n\nEffect: +1 military factory.", ['tobolsk_grain']),
    F('loyal_rations', 'Rations by Reliability', 16, 4, 49, 'economy',
      "Bread by category: reliable, doubtful, enemy.\n\nEffect: +5% stability, Fear of the Commissar grows.", ['tobolsk_grain']),
    F('commissariat_plan', "The Commissariat's Plan", 15, 5, 105, 'industry',
      "A five-year plan drawn up by policemen.\n\nEffect: +5% construction speed, +5% factory output.", ['sverdlovsk_arms', 'loyal_rations']),

    # --- the army (military, x 18)
    F('nkvd_troops', 'NKVD Troops', 18, 1, 49, 'military',
      "The republic's army is the Commissariat's own internal troops.\n\nEffect: +army experience.", ['commissar']),
    F('border_guards', 'The Border Guard Divisions', 18, 2, 49, 'military',
      "NKVD border guards, the best-equipped soldiers in the Urals.\n\nEffect: +5% defence.", ['nkvd_troops']),
    F('ural_passes', 'Hold the Ural Passes', 18, 3, 49, 'military',
      "West lies the Reichskommissariat, east lies Popov. The passes must hold.\n\nEffect: forts at the border.", ['border_guards']),
    F('tankograd_tanks', 'Tanks for the Organs', 18, 4, 49, 'military',
      "Tankograd's tanks go to NKVD units, not the army.\n\nEffect: tanks added to the stockpile.", ['ural_passes']),
]

build('csr', 'Popov - Central Siberian Republic (CSR)', 'CSR', 'wif_csr_focus', CSR, 'csr_map.json')
build('fes', 'Stalin - Far Eastern Union (FES)', 'FES', 'wif_fes_focus', FES, 'fes_map.json')
build('wsm', 'Yagoda - West Siberian Marxist Republic (WSM)', 'WSM', 'wif_wsm_focus', WSM, 'wsm_map.json', target=2375)
