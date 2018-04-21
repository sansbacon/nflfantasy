'''
pipelines/dk.py
functions to transform dk data for insertion into database, etc.
'''

# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging

logging.getLogger(__name__).addHandler(logging.NullHandler())

def game_id(p, games):
    '''
    
    Args:
        g: 
        games: 

    Returns:

    '''
    if p['tid'] == p['htid']:
        game = [g for g in games if g['source_home_team_code'] == p['htabbr']][0]
    elif p['tid'] == p['atid']:
        game = [g for g in games if g['source_away_team_code'] == p['atabbr']][0]
    return game['source_game_id']

def player_team(p):
    '''
    
    Args:
        self: 
        player: 

    Returns:
        player team code, opp team code
    '''
    if p['tid'] == p['htid']:
        return (p['htabbr'], p['atabbr'])
    elif p['tid'] == p['atid']:
        return (p['atabbr'], p['htabbr'])
    else:
        raise ValueError('cannot find team code')

def weekly_dk_games_table(games, seas, week, main_slate, slate_name):
    '''
    Converts data from dk salaries page

    Arguments:
        players: list of dict
        seas: 2017, 2016, etc.
        week: 1, 2, 3, etc.

    Returns:
        list of dict
    '''
    fixed = []
    slate_size = len(games)
    for game in games:
        f = game.copy()
        f['season_year'] = seas
        f['week'] = week
        f['slate_size'] = slate_size
        f['slate_name'] = slate_name
        f['main_slate'] = main_slate
        fixed.append(f)
    return fixed

def weekly_dk_players_table(players, games, seas, week):
    '''
    Converts data from dk salaries page

    Arguments:
        players: list of dict
        seas: 2017, 2016, etc.
        week: 1, 2, 3, etc.

    Returns:
        list of dict
    '''
    fixed = []
    for p in players:
        f = {'season_year': seas, 'week': week}
        f['source_player_name'] = p['fn'] + ' ' + p['ln']
        f['source_player_id'] = p['pid']
        f['source_player_code'] = p['pcode']
        f['source_player_position'] = p['pn']
        f['source_team_code'], f['source_opp_code'] = player_team(p)
        f['source_game_id'] = game_id(p, games)
        f['opp_rating'] = p['or']
        f['salary'] = p['s']
        f['ppg'] = p['ppg']
        f['injury'] = p['i']
        fixed.append(f)
    return fixed

def dk_slate_players_table(players, seas, week, slate):
    '''
    
    Args:
        players: 
        seas: 
        week: 
        slate: 

    Returns:

    '''
    fixed = []
    for p in players:
        f = {'season_year': seas, 'week': week, 'slate': slate}
        f['source_player_name'] = p['Name']
        f['source_player_id'] = p['ID']
        f['source_team_code'] = p['TeamAbbrev']
        f['source_player_position'] = p['Position']
        f['salary'] = p['Salary']
        fixed.append(f)
    return fixed

def valornone(val):
    '''
    
    Args:
        val: 

    Returns:

    '''
    if val == '':
        return None
    else:
        return val


if __name__ == '__main__':
    pass