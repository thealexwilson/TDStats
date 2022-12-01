import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict

=query(A1:M30, "select D, C where B Contains 'ADZ1LAAA'", 1)
=query(stats!A1:C9, "select D, C where B Contains 'ADZ1LAAA'", 1)

dfs =pd.read_excel("Boomer Bowl TDM Stats.xlsx",sheet_name=None)
matches = defaultdict(dict)

# print("dfs: ")
# print(dfs)
for k, df in dfs.items():
    # print("df: ")
    # print(df)
    # print("k: ")
    # print(k)
    if k == 'Rankings':
        pass
    opponent = ''
    for row in df.itertuples():
        # print("row: ")
        # print(row)
        rv = row[1]
        # print("rv: ")
        # print(rv)
        blank = type(rv) == float and np.isnan(rv)
        if rv == 'Map':
            # print("row: ")
            # print(row)

            # print("row[0]: ")
            # print(row[0]+2)

            # print("row[0]+6")
            # print(row[0]+6)

            # print("df.iloc[row[0]+2:row[0]+6,:7].copy()")
            # print(df.iloc[row[0]+2:row[0]+6,:7].copy())

            dfn = df.iloc[row[0]+2:row[0]+6,:7].copy()
            # print("list(df.iloc[row[0]+1,:7])")
            # print(list(df.iloc[row[0]+1,:7]))

            dfn.columns = list(df.iloc[row[0]+1,:7])
            # print("dfn: ")
            # print(dfn)

            map_name = row[2]
            kval = tuple(sorted([k,opponent]) + [map_name])
            matches[kval][k] = dfn
            # print("matches: ")
            # print(matches)
        if rv == 'Match':
            opponent = row[2].split()[-1]
            if opponent == 'mode?':
                opponent = 'Mode'
            if opponent == 'X-Rated':
                opponent = 'XRated'
            # print(k, opponent)
            # print("matches: ")
            # print('\t',matches)
    print()
maps = defaultdict(list)
for k,v in matches.items():
    ting = [v2.mean(0) for k2,v2 in v.items()]
    maps[k[-1]].append(ting)
cols = list(maps[list(maps.keys())[0]][0][0].keys())
df_maps = pd.DataFrame({k:np.mean(sum(v,[]),axis=0) for k,v in maps.items()}).T
df_maps.columns = cols
df_maps.sort_values('Damage Given')
{k: list(v.keys()) for k,v in matches.items() if len(v.keys()) == 1}
aliases = {
    'm:(es':'miles',
    'miles of shit':'miles',
    'fuckin miles':'miles',
    't41TG':'t41TG',
    'ᵠᶠᴸt41TG':'t41TG',
    'miles morales SPIDERMAN':'miles',
    'davE':'icel0re',
    '1999 icel0re':'icel0re',
    'konz':'konfuzed',
    'a1 sotrix':'sotrix',
    'zog':'zig',
    'imaloser':'sotrix',
    'Raul':'raul',
}
tot_tables = {k: pd.concat(v.values()).set_index('Player') for k,v in matches.items()}
for k,v in tot_tables.items():
    v.index = pd.Index([aliases.get(_,_) for _ in v.index],name='Player')
nrm_tables = {k:v/v.mean(0) for k,v in tot_tables.items()}

for k,v in nrm_tables.items():
    v['map'] = k[2]
    v['team1'] = k[1]
    v['team2'] = k[0]
v = nrm_tables[('Mode',  'SavageZ',  'dredwerkz')]
dft = pd.concat(nrm_tables.values()).sort_values('Damage Given',0,False).drop(['Net F/D','Net Damage'],1)

dft['NormNet Damage'] = dft['Damage Given']-dft['Damage Taken']
dft['Norm(FmD)'] = dft['Frags']-dft['Deaths']
dft['sNetE'] = dft['Frags'] + ( dft['Damage Given']/ 181.2 ) + ( dft['Deaths'] / -3.5 ) + ( dft['Damage Taken'] / -275.1 )
dft['sNetE'] = dft['Frags'] + ( dft['Damage Given'] ) + ( dft['Deaths'] / -3.5 ) + ( dft['Damage Taken'] / -1.5 )
dft = dft.sort_values('sNetE',0,False)
dft.to_csv('xzist_out2.csv')
dft
df_ci = dft.drop(['map','team1','team2'],1).groupby('Player')
df_ci = 1.96*df_ci.std()/np.sqrt(df_ci.count())
dft2 = dft.groupby('Player').mean().sort_values('sNetE',0,False)
dft2['lb_snet'] = dft2['sNetE'] - df_ci['sNetE']
dft2['ub_snet'] = dft2['sNetE'] + df_ci['sNetE']
dft2.to_csv('xzist_out.csv')
dft2
df_ci.std()