from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
# import fetch_google_sheet_data
# dfs = fetch_google_sheet_data.main()
import pandas_stats_data


match_list = pandas_stats_data.main()
matches = defaultdict(dict)

for match in match_list:
    map_name = match["map"]
    df = match["df"]
    team1 = match["teams"][0]
    team2 = match["teams"][1]

    for row in df.itertuples():
        team1_rows = df.loc[df['Team Name'] == team1]
        new_df = team1_rows.copy()
        new_df = new_df.append(df.loc[df['Team Name'] == team2])
        columns = df.columns[:8]
        new_df = new_df[columns]
        # print("new_df: ")
        # print(new_df)

        kval = tuple(sorted(match['teams']) + [map_name])
        matches[kval][team1] = new_df
        print("matches: ")
        print('\t',matches)
    print()

    maps = defaultdict(list)
    for k, v in matches.items():
        ting = [v2.mean(0) for k2, v2 in v.items()]
        maps[k[-1]].append(ting)
    cols = list(maps[list(maps.keys())[0]][0][0].keys())
    df_maps = pd.DataFrame({ k:np.mean(sum(v, []), axis = 0) for k, v in maps.items() }).T
    df_maps.columns = cols
    df_maps.sort_values('Damage Dealt')
    { k: list(v.keys()) for k, v in matches.items() if len(v.keys()) == 1 }
    
    # TODO: Remove this - we already doing this
    # Just need to make sure we capitalized all the names in the output
    # aliases = {
    #     'm:(es':'miles',
    #     'miles of shit':'miles',
    #     'fuckin miles':'miles',
    #     't41TG':'t41TG',
    #     'ᵠᶠᴸt41TG':'t41TG',
    #     'miles morales SPIDERMAN':'miles',
    #     'davE':'icel0re',
    #     '1999 icel0re':'icel0re',
    #     'konz':'konfuzed',
    #     'a1 sotrix':'sotrix',
    #     'zog':'zig',
    #     'imaloser':'sotrix',
    #     'Raul':'raul',
    # }
    aliases = {
        "vig1lante": 'VIG1LANTE',
        "zɥdoɹԀ": 'ZHPORP',
        "hotmessexpress": 'HOTMESSEXPRESS',
        "Warden": 'WARDEN',
        "XZIST": 'XZIST',
        "ziGGeh": 'ZIGGEH',
        "Rey": 'REY',
        "thundeR": 'THUNDER',
        "adz1LaAa": 'ADZ1LAAA',
        "Moody": 'MOODY',
        "zombie": 'ZOMBIE',
        "sotrix": 'SOTRIX',
        "aW.phalaer": 'AW.PHALAER',
        "butcher": 'BUTCHER',
        "ouija": 'OUIJA',
        "MILFMAGNET69": 'MILFMAGNET69',
        "Joe": 'JOE',
        "torrin": 'TORRIN',
        "aW.dakinaw": 'AW.DAKINAW',
        "Lampyre": 'LAMPYRE',
        "vibration": 'VIBRATION',
        "machine": 'MACHINE',
        "]69[MzHero♡": 'MZHEROINE',
        "C@NIP": 'C@NIP'
    }
    tot_tables = { k: pd.concat(v.values()).set_index('Player Name') for k, v in matches.items() }
    for k, v in tot_tables.items():
        v.index = pd.Index([aliases.get(_,_) for _ in v.index],name='Player Name')

    nrm_tables = { k:v/v.mean(0) for k, v in tot_tables.items() }
    # print("nrm_tables: ")
    # print(nrm_tables)

    for k, v in nrm_tables.items():
        v['map'] = k[2]
        v['team1'] = k[1]
        v['team2'] = k[0]
    # print("nrm_tables: ")
    # print(nrm_tables)
    # v = nrm_tables[('Mode',  'SavageZ',  'dredwerkz')]
    dft = pd.concat(nrm_tables.values()).sort_values('Damage Dealt', 0, False).drop(['KDR', 'Net Damage'], 1)
    # dft = pd.concat(nrm_tables.values()).sort_values('Damage Dealt', 0, False).drop(['KDR'], 1)

    dft['NormNet Damage'] = dft['Damage Dealt']-dft['Damage Taken']
    dft['Norm(FmD)'] = dft['Kills']-dft['Deaths']
    dft['sNetE'] = dft['Kills'] + ( dft['Damage Dealt']/ 181.2 ) + ( dft['Deaths'] / -3.5 ) + ( dft['Damage Taken'] / -275.1 )
    dft['sNetE'] = dft['Kills'] + ( dft['Damage Dealt'] ) + ( dft['Deaths'] / -3.5 ) + ( dft['Damage Taken'] / -1.5 )
    dft = dft.sort_values('sNetE',0,False)
    dft.to_csv('xzist_out2.csv')
    dft
    df_ci = dft.drop(['map','team1','team2'],1).groupby('Player Name')
    df_ci = 1.96*df_ci.std()/np.sqrt(df_ci.count())
    dft2 = dft.groupby('Player Name').mean().sort_values('sNetE',0,False)
    dft2['lb_snet'] = dft2['sNetE'] - df_ci['sNetE']
    dft2['ub_snet'] = dft2['sNetE'] + df_ci['sNetE']
    dft2.to_csv('xzist_out.csv')
    dft2
    df_ci.std()