#optdiv.py
# testing optimized diverse lineups
import pprint

import pandas as pd
import numpy as np

from nflfantasy.optimizers.dk import *

dko = NFLOptimizerDK()

df = pd.read_csv('/home/sansbacon/workspace/nflfantasy/optimizers/data2017.csv').dropna()
df['salrk'] = df.groupby(['year', 'week', 'pos'])['sal'].rank(ascending=False)
df['posrk'] = df.groupby(['year', 'week', 'pos'])['proj'].rank(ascending=False)
df['actual'] = df['proj']
df['proj'] = df['proj'] - ((df['proj']/4 * np.random.random(len(df))))
df = df.sort_values(['year', 'week', 'team', 'pos', 'proj'],
                    ascending=[True, True, True, True, False])
week = 1
all_players = [Player(p) for p in df[df['week'] == week].T.to_dict().values()]
lineups = list(dko.optimize(all_players, n=1))
for _ in range(149):
     lineups.append(dko._optimize_diverse(all_players, lineups, overlap=5))

# convert lineups to dataframe
results = []
for idx, l in enumerate(lineups):
    lineup_id = idx + 1
    for p in l.players:
        d = p.__dict__.copy()
        d['lineup_id'] = lineup_id
        results.append(d)
rdf = pd.DataFrame(results)
rdf = rdf.sort_values(['lineup_id', 'pos'])
rdf.to_csv('/home/sansbacon/rdf.csv', index=False)
