# playdraftsim.py

from collections import defaultdict
from operator import itemgetter
import pickle
import pprint
import random


class PlayDraftSim(object):

    def __init__(self):
        # setup, have 6 teams
        self.position_limits = {'QB': 1, 'RB': 2, 'WR': 2}
        self.draft_order = [1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 
                       1, 2, 3, 4, 5, 6, 6, 5, 4, 3, 2, 1, 
                       1, 2, 3, 4, 5, 6]

        # get draft data      
        with open('/home/sansbacon/draftw13.pkl', 'rb') as infile:
            self.dpl = pickle.load(infile)
    
        # divide into qbs/rbs/wrs
        self.qbs = [p for p in list(self.dpl.values()) if p['source_player_position'] == 'QB']
        self.rbs = [p for p in list(self.dpl.values()) if p['source_player_position'] == 'RB']
        self.wrs = [p for p in list(self.dpl.values()) if p['source_player_position'] in ['WR', 'TE']]


        self.pool = {'QB': sorted(self.qbs, key=itemgetter('projection'), reverse=True),
                     'RB': sorted(self.rbs, key=itemgetter('projection'), reverse=True),
                     'WR': sorted(self.wrs, key=itemgetter('projection'), reverse=True)
                    }
    def draft(self, nteams=6):
        # now start the draft
        teams = {i: {'QB': [], 'RB': [], 'WR': [], 'Positions': []} 
                 for i in range(1, nteams+1)}

        for pick in self.draft_order:
            # randomly order positions at start of turn
            positions = list(self.position_limits.keys())
            random.shuffle(positions)

            # take first position off the stack
            pos = positions.pop(0)
            
            # you can use this position if you are below position limits
            # otherwise have to try next position, see if below limits
            if len(teams[pick][pos]) < self.position_limits[pos]:
                player = self.pool[pos].pop(0)
                teams[pick][pos].append(player)
                teams[pick]['Positions'].append(player.get('source_player_position'))
            else:
                pos = positions.pop(0)
                if len(teams[pick][pos]) < self.position_limits[pos]:
                    player = self.pool[pos].pop(0)
                    teams[pick][pos].append(player)
                    teams[pick]['Positions'].append(player.get('source_player_position'))
                else:
                    pos = positions.pop(0)
                    if len(teams[pick][pos]) < self.position_limits[pos]:
                        player = self.pool[pos].pop(0)
                        teams[pick][pos].append(player)
                        teams[pick]['Positions'].append(player.get('source_player_position'))
        return teams

    def draft_results(self, teams):
        # sum the results
        team_results = {i: {'Total': 0.0, 'QB': 0.0, 'RB': 0.0, 'WR': 0.0} for i in range(1, len(list(teams.keys()))+1)}

        for team_id, team in teams.items():
            for pos, players in team.items():
                if pos in self.position_limits.keys():
                    for player in players:           
                        team_results[team_id][pos] += player.get('projection', 0)
                        team_results[team_id]['Total'] += player.get('projection', 0)
                        team_results[team_id]['Positions'] = team['Positions']
        return team_results

    def print_draft_results(self, draft_results):
        pprint.pprint(sorted(list(draft_results.values()), key=itemgetter('Total'), reverse=True))


if __name__ == '__main__':
    import pandas as pd
    import numpy as np

    results = []
    for i in range(50000):
        sim = PlayDraftSim()
        teams = sim.draft()
        for team_id, team in sim.draft_results(teams).items():
            order = '_'.join(team['Positions'])
            results.append({'score': team.get('Total'), 'order': order, 'draftpos': team_id})

    df = pd.DataFrame(results)
    grouped = df.groupby(['draftpos', 'order']).aggregate(np.mean)
    print(grouped)
    grouped.to_csv('/home/sansbacon/draftsim.csv')
