# playdraft_sim.py
# simulates draft with their projections

from operator import itemgetter
import pickle
import pprint
import random

# setup, have 6 teams
nteams = 6
position_limits = {'QB': 1, 'RB': 2, 'WR': 2}
draft_order = [1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 
               1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 
               1, 2, 3, 4, 5, 6]

# get draft data      
with open('/home/sansbacon/DRAFT/draft-w14_15-pool.pkl', 'rb') as infile:
    dpl = pickle.load(infile)
    
# divide into qbs/rbs/wrs
qbs = [p for p in dpl if p['source_player_position'] == 'QB']
rbs = [p for p in dpl if p['source_player_position'] == 'RB']
wrs = [p for p in dpl if p['source_player_position'] in ['WR', 'TE']]

pool = {'QB': sorted(qbs, key=itemgetter('projection'), reverse=True),
        'RB': sorted(rbs, key=itemgetter('projection'), reverse=True),
        'WR': sorted(wrs, key=itemgetter('projection'), reverse=True)
}

# now start the draft
teams = {i: {'QB': [], 'RB': [], 'WR': [], 'Positions': []} 
         for i in range(1, nteams+1)}

for pick in draft_order:
    # randomly order positions at start of turn
    positions = list(position_limits.keys())
    random.shuffle(positions)

    # take first position off the stack
    pos = positions.pop(0)
    
    # you can use this position if you are below position limits
    # otherwise have to try next position, see if below limits
    if len(teams[pick][pos]) < position_limits[pos]:
        player = pool[pos].pop(0)
        teams[pick][pos].append(player)
        teams[pick]['Positions'].append(player.get('source_player_position'))
    else:
        pos = positions.pop(0)
        if len(teams[pick][pos]) < position_limits[pos]:
            player = pool[pos].pop(0)
            teams[pick][pos].append(player)
            teams[pick]['Positions'].append(player.get('source_player_position'))
        else:
            pos = positions.pop(0)
            if len(teams[pick][pos]) < position_limits[pos]:
                player = pool[pos].pop(0)
                teams[pick][pos].append(player)
                teams[pick]['Positions'].append(player.get('source_player_position'))

# sum the results
team_results = {i: {'Total': 0.0, 'QB': 0.0, 'RB': 0.0, 'WR': 0.0} for i in range(1, nteams+1)}

for team_id, team in teams.items():
    for pos, players in team.items():
        if pos in position_limits.keys():
            for player in players:           
                team_results[team_id][pos] += player.get('projection', 0)
                team_results[team_id]['Total'] += player.get('projection', 0)
                team_results[team_id]['Positions'] = team['Positions']
            
pprint.pprint(sorted(list(team_results.values()), key=itemgetter('Total'), reverse=True))