
df = pd.read_csv('3-man-sim.csv', index_col=0)
prob = LpProblem('Daily Fantasy Sports', LpMaximize)

r1 = LpVariable.dicts(
                'r1', df.index,
                lowBound=0,
                upBound=1,
                cat=LpInteger
            )

r2 = LpVariable.dicts(
                'r2', df.index,
                lowBound=0,
                upBound=1,
                cat=LpInteger
            )
        
prob += lpSum([(df.loc[p,'pts'] * r1[p]) + (df.loc[p,'pts'] * r2[p])
               for p in df.index])
prob += lpSum([r1[p] for p in df.index]) == 1
prob += lpSum([r2[p] for p in df.index]) == 1
prob += lpSum([df.loc[p,'r1p'] * r1[p] for p in df.index]) == 1
prob += lpSum([df.loc[p,'r2p'] * r2[p] for p in df.index]) >= .4

prob.solve()

for idx in df.index:
    if r1[idx].value() == 1:
        print('1', df.loc[idx])
    elif r2[idx].value() == 1:
        print('2', df.loc[idx])


###########################################
# trying to use dictionary approach

df = pd.read_csv('3-man-sim.csv', index_col=0)
maxp = 18

# x is numeric, represents round number
d = {x: LpVariable.dicts("r{}".format(x), df.index, lowBound=0, upBound=1, cat=LpInteger) 
      for x in range(1, maxp + 1)}

prob = LpProblem('Daily Fantasy Sports', LpMaximize)

# objective function
prob += lpSum([df.loc[p,'pts'] * d[x][p] for x in range(1, maxp + 1) for p in df.index])

# a player can only be chosen once
for p in df.index:
    prob += lpSum([d[x][p] for x in range(1, maxp + 1)]) <= 1

# there must be one player chosen in each round
for x in range(1, maxp + 1):      
    k = 'r{}p'.format(x)
    prob += lpSum([d[x][p] for p in df.index]) == 1
    prob += lpSum([df.loc[p,k] * d[x][p] for p in df.index]) >= 1 - (float(x)/20)

prob.solve()

for x in range(1, maxp + 1):
    for p in df.index:
        if d[x][p].value() == 1:
            print(x, p, df.loc[p, 'pts'], df.loc[p, 'r{}p'.format(x)])
            
######################

import pandas as pd

df = pd.read_csv('3-man-sim.csv', index_col=0)
rounds = 18


