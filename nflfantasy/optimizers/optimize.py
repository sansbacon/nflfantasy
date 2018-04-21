#!/usr/bin/python

# this solution is almost wholly based off
# https://github.com/swanson/degenerate and mrnitrate's fork

import csv

from ortools.linear_solver import pywraplp
from pulp import *

from orm import *
from constants import *
from nfl.projections import alter_projection

'''
Load Salary and Prediction data from csv's
'''
def load_players(players, projection_site, projection_formula, team_exclude=[], player_exclude=[], random=True):
    '''
    Takes list of player dicts, returns list of Player objects
    :param players(list): of player dict
    :return: all_players(list): of Player
    '''
    all_players = []

    if projection_site == 'dk':
        for p in players:
            oppos = str(p.get('Opposing_TeamFB', '').replace('@', ''))
            pos = str(p.get('Position'))
            if pos == 'D':
                pos = str('DST')
            team = str(p.get('Team'))
            player_name = str(p.get('Player_Name'))
            code = str('{}_{}'.format(player_name, pos))
            proj = alter_projection(p, keys=['AvgPts', 'Ceiling', 'Floor'], projection_formula=projection_formula, randomize=True)

            if team in team_exclude:
                continue
            elif player_name in player_exclude:
                continue
            else:
                all_players.append(ORToolsPlayer(proj=proj, matchup=p.get('Opposing_TeamFB'), opps_team=oppos, code=code, pos=pos, name=player_name, cost=p.get('Salary'), team=team))

    return all_players

def pulp_optimizer(all_players):
    '''
    Right now assumes players are from fantasylabs
    Based on https://github.com/sansbacon/pydfs-lineup-optimizer
    '''
    
    wanted = ['Player_Name', 'Team', 'Position', 'Salary', 'AvgPts']

    pool = [{k:v for k,v in p.items() if k in wanted} for p in all_players]
    players = [ORToolsPlayer(proj=p['AvgPts'], pos=p['Position'], name=p['Player_Name'], cost=p['Salary'], team=p['Team'], marked=0) for p in pool]

    x = LpVariable.dicts('table', players, lowBound=0, upBound=1, cat=LpInteger)
    prob = LpProblem('DFS', LpMaximize)

    # objective function: maximize projected points
    prob += sum([p.proj * x[p] for p in players])

    # salary cap constraint
    prob += sum([p.cost * x[p] for p in players]) <= 50000

    # roster size constraint
    prob += sum([x[p] for p in players]) == 9

    # positional constraints
    prob += sum([x[p] for p in players if p.pos == 'QB']) == 1
    prob += sum([x[p] for p in players if p.pos == 'RB']) >= 2
    prob += sum([x[p] for p in players if p.pos == 'WR']) >= 3
    prob += sum([x[p] for p in players if p.pos == 'TE']) >= 1
    prob += sum([x[p] for p in players if p.pos == 'D']) == 1
    prob += sum([x[p] for p in players if p.pos == 'WR']) <= 4
    prob += sum([x[p] for p in players if p.pos == 'RB']) <= 3
    prob += sum([x[p] for p in players if p.pos == 'TE']) <= 2
    prob += sum([x[p] for p in players if p.pos == 'TE']) <= 2

    # player excludes
    prob += sum([p.marked * x[p] for p in players]) == 0

    # player locks
    prob += sum([p.locked * x[p] for p in players]) == sum(p.locked for p in players)

    # solve and print
    prob.solve()
    roster = ORToolsRoster()
    for p in players:
        if x[p].value() == 1.0:
            roster.add_player(p)

    return roster

def run_solver(all_players, depth, iteration_id, min_teams=2, stack_wr=None, stack_te=None):
    '''
    Arguments:

    Returns:
        rosters(list): of Rosters
    '''
    solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

    variables = []
    for player in all_players:
        variables.append(solver.IntVar(0, 1, player.code))

    '''
    Setup Maximization over player point projections
    '''
    objective = solver.Objective()
    objective.SetMaximization()
    for i, player in enumerate(all_players):
        objective.SetCoefficient(variables[i], player.proj)

    '''
    Add Salary Cap Constraint
    '''
    salary_cap = solver.Constraint(SALARY_CAP-1000, SALARY_CAP)
    for i, player in enumerate(all_players):
        salary_cap.SetCoefficient(variables[i], player.cost)

    '''
    Add Player Position constraints including flex position
    '''
    flex_rb = solver.IntVar(0, 1, 'Flex_RB')
    flex_wr = solver.IntVar(0, 1, 'Flex_WR')
    flex_te = solver.IntVar(0, 1, 'Flex_TE')

    solver.Add(flex_rb+flex_wr+flex_te==1)

    for position, limit in POSITION_LIMITS_FLEX:
        ids, players_by_pos = zip(*filter(lambda (x,_): x.pos in position, zip(all_players, variables)))
        if position == 'WR':
            solver.Add(solver.Sum(players_by_pos) == limit+flex_wr)
        elif position == 'RB':
            solver.Add(solver.Sum(players_by_pos) == limit+flex_rb)
        elif position == 'TE':
            solver.Add(solver.Sum(players_by_pos) == limit+flex_te)
        else :
            solver.Add(solver.Sum(players_by_pos) == limit)

    '''
    Add remove previous solutions constraint and loop to generate X rosters
    '''
    rosters = []
    for x in xrange(depth):
        if rosters :
            ids, players_from_roster = zip(*filter(lambda (x,_): x in rosters[-1].sorted_players()  , zip(all_players, variables)))
            ids, players_not_from_roster = zip(*filter(lambda (x,_): x  not in rosters[-1].sorted_players()  , zip(all_players, variables)))
            solver.Add(solver.Sum(players_not_from_roster)+solver.Sum(1-x for x in players_from_roster)>=9)
        solution = solver.Solve()
        if solution == solver.OPTIMAL:
            roster = ORToolsRoster(iteration_id=iteration_id, roster_id=x)
            for i, player in enumerate(all_players):
                if variables[i].solution_value() == 1:
                    roster.add_player(player)
            rosters.append(roster)
        else:
            raise Exception('No solution error')

    return rosters

def write_bulk_import_csv(rosters, fn):
    with open(fn, 'wb') as csvfile:
        writer = csv.writer(csvfile,delimiter=',',quotechar='"',quoting=csv.QUOTE_NONNUMERIC)
        for roster in rosters:
            writer.writerow([x.name for x in roster.sorted_players()])

if __name__ == "__main__":
    pass