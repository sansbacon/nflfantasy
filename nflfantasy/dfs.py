
'''
dfs.py
Takes statistics and calculates fantasy points
Borrowed from https://github.com/kacperadach/draftkings_points_scripts
Use for calculating dk points from gamecenter API feed - single game
Use for calculating dk points from gamecenter API feed - single game
'''

import json


def dk_points(self, pos, draft_kings_stats):
    points = 0
    if pos != 'DEF':
        points += (int(draft_kings_stats['6']) * 4)
        points += (int(draft_kings_stats['5']) * 0.04)
        if int(draft_kings_stats['5']) >= 300:
            points += 3
        points -= (int(draft_kings_stats['7']) * 1)
        points += (int(draft_kings_stats['14']) * 0.1)
        points += (int(draft_kings_stats['15']) * 6)
        if int(draft_kings_stats['14']) >= 100:
            points += 3
        points += (int(draft_kings_stats['21']) * 0.1)
        points += (int(draft_kings_stats['20']) * 1)
        points += (int(draft_kings_stats['22']) * 6)
        if int(draft_kings_stats['21']) >= 100:
            points += 3
        points += (int(draft_kings_stats['28']) * 6)
        points -= (int(draft_kings_stats['30']) * 1)
        points += (int(draft_kings_stats['32']) * 2)
        points += (int(draft_kings_stats['29']) * 6)

    return points

def dk_scoring(player):

    dkpoints = 0

    offense_values = {
        'rushing_td': 6,
        'receiving_td': 6,
        'recovery_td': 6,
        'passing_td': 4,
        'passing_yards': .04,
        'rushing_yards': .10,
        'passing_yards': .10,
        'fumbles': -1,
        'interceptions': -1,
        'two_point_conversions': 2,
    }

    offensive_bonuses = {
        'passing_yards': {'threshold': 300, 'bonus': 3},
        'rushing_yards': {'threshold': 100, 'bonus': 3},
        'receiving_yards': {'threshold': 100, 'bonus': 3},
    }

    defense_values = {
        'sacks': 1,
        'interceptions': 2,
        'fumbles_recovered': 2,
        'td': 6,
        'safety': 2,
        'blocked_kick': 2,
    }

    defensive_bonuses = [(0, 10), (6, 7), (13, 4), (20, 1), (27, 0), (34, -1), (35, -4)]

    if player['position'] == 'DST':
        pass

    else:
        for key in offensive_values:
            if key in player and player[key] > 0:
                dkpoints += player[key] * offensive_values[key]    

        for key in offensive_bonuses:
            if key in player and player[key] >= offensive_bonuses[key]['threshold']:
                dkpoints += offensive_bonuses[key]['value'] 

def player_points(self, players):

    for player in players:
        pos = player['position']
        stats = player['stats']

        draft_kings_stats = {}

        for x in xrange(91):
            try:
                num_str = str(x)
                draft_kings_stats[num_str] = stats[num_str]
            except KeyError:
                draft_kings_stats[num_str] = '0'

        player['dk_points'] = dk_points(pos, draft_kings_stats)    

    return players
    
if __name__=='__main__':
    pass
