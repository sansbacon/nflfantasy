# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging

from nfl.teams import long_to_code


logging.getLogger(__name__).addHandler(logging.NullHandler())


def weekly_rankings_table(rankings, season_year):
    '''
    Converts data from fantasypros.com weekly rankings page for insertion into weekly_rankings table
    
    Args:
        results: list of dict

    Returns:
        list of dict
    '''
    for idx, player in enumerate(rankings):
        rankings[idx]['season_year'] = season_year
        rankings[idx]['source'] = 'fantasypros'
        rankings[idx]['position'] = player.get('pos', '').upper()
        rankings[idx].pop('pos', None)
        if player['position'] == 'DST':
            rankings[idx]['team_code'] = long_to_code(player['player'])
        rankings[idx]['source_player_name'] = player['player']
        rankings[idx].pop('player', None)
        rankings[idx].pop('bye', None)
        rankings[idx].pop('last_updated', None)
        if ' ' in player.get('opp', ''):
            rankings[idx]['opp'] = player['opp'].split()[-1]
    return rankings


def adp2012(content, db, season_year, scoring_format):
    pos = fpros_playercode_positions(db)
    pid = fpros_playercode_playerid(db)
    players = []
    soup = BeautifulSoup(content, 'lxml')
    for tr in soup.find('table', {'id': 'data'}).find('tbody').find_all('tr'):
        player = {'source': 'fantasypros',
                  'source_league_type': scoring_format,
                  'season_year': season_year}
        tds = tr.find_all('td')

        # exclude stray rows that don't have player data
        if len(tds) == 1:
            continue

        # try to find player id, name, and code
        for idx, a in enumerate(tr.find_all('a')):
            if idx == 0:
                player['source_player_code'] = a['href'].split('/')[-1].split('.php')[0]
                player['source_player_name'] = a.text
            elif idx == 1:
                player['source_team_code'] = a.text

        if not player.get('source_team_code'):
            player['source_team_code'] = 'UNK'

        # fix for DST
        if 'defense' in player['source_player_code']:
            player['source_player_position'] = 'DST'
            player['source_player_name'] += ' Defense'

        # get remaining stats
        player['adp'] = float(tds[-1].text)
        if not player.get('source_player_position'):
            player['source_player_position'] = \
                pos.get(player['source_player_code'], 'UNK')

        # get source player id
        player['source_player_id'] = pid.get(player['source_player_code'], 'UNK')

        # add to list
        players.append(player)

    return players


def adp2013(content, db, season_year=2013, scoring_format='ppr'):
    pos = fpros_playercode_positions(db)
    pid = fpros_playercode_playerid(db)
    players = []
    soup = BeautifulSoup(content, 'lxml')
    for tr in soup.find('table', {'id': 'data'}).find('tbody').find_all('tr'):
        player = {'source': 'fantasypros',
                  'source_league_type': scoring_format,
                  'season_year': season_year}
        tds = tr.find_all('td')

        # exclude stray rows that don't have player data
        if len(tds) == 1:
            continue

        # try to find player id, name, and code
        for idx, a in enumerate(tr.find_all('a')):
            if idx == 0:
                player['source_player_code'] = a['href'].split('/')[-1].split('.php')[0]
                player['source_player_name'] = a.text
            elif idx == 1:
                player['source_team_code'] = a.text

        if not player.get('source_team_code'):
            player['source_team_code'] = 'UNK'

        # fix for DST
        if 'defense' in player['source_player_code']:
            player['source_player_position'] = 'DST'
            player['source_player_name'] += ' Defense'

        # get remaining stats
        player['adp'] = float(tds[-1].text)
        if not player.get('source_player_position'):
            player['source_player_position'] = \
                pos.get(player['source_player_code'], 'UNK')

        posrk = tds[2].text
        player['position_rank'] = int(''.join([s for s in posrk if s.isdigit()]))

        # get source player id
        player['source_player_id'] = pid.get(player['source_player_code'], 'UNK')

        # add to list
        players.append(player)

    return players


def adp2014(content, db, season_year=2014, scoring_format='ppr'):
    pos = fpros_playercode_positions(db)
    pid = fpros_playercode_playerid(db)
    players = []
    soup = BeautifulSoup(content, 'lxml')
    for tr in soup.find('table', {'id': 'data'}).find('tbody').find_all('tr'):
        player = {'source': 'fantasypros',
                  'source_league_type': scoring_format,
                  'season_year': season_year}
        tds = tr.find_all('td')

        # exclude stray rows that don't have player data
        if len(tds) == 1:
            continue

        # try to find player id, name, and code
        for idx, a in enumerate(tr.find_all('a')):
            if idx == 0:
                player['source_player_code'] = a['href'].split('/')[-1].split('.php')[0]
                player['source_player_name'] = a.text
            elif idx == 1:
                player['source_team_code'] = a.text

        # fix for DST
        if 'defense' in player['source_player_code']:
            player['source_player_position'] = 'DST'
            player['source_team_code'] = long_to_code(player['source_player_name'].split(' Defense')[0].strip())

        if not player.get('source_team_code'):
            player['source_team_code'] = 'UNK'

        # get remaining stats
        player['adp'] = float(tds[-1].text)
        if not player.get('source_player_position'):
            player['source_player_position'] = \
                pos.get(player['source_player_code'], 'UNK')

        # position and posrk
        posrk = tds[2].text
        player['source_player_position'] = ''.join([s for s in posrk if not s.isdigit()])
        player['position_rank'] = int(''.join([s for s in posrk if s.isdigit()]))

        # get source player id
        player['source_player_id'] = pid.get(player['source_player_code'], 'UNK')


def adp2015(content, db, season_year=2015, scoring_format='ppr'):
    pos = fpros_playercode_positions(db)
    pid = fpros_playercode_playerid(db)
    players = []
    soup = BeautifulSoup(content, 'lxml')
    for tr in soup.find('table', {'id': 'data'}).find('tbody').find_all('tr'):
        player = {'source': 'fantasypros',
                  'source_league_type': scoring_format,
                  'season_year': season_year}
        tds = tr.find_all('td')

        # exclude stray rows that don't have player data
        if len(tds) == 1:
            continue

        # try to find player id, name, and code
        for idx, a in enumerate(tr.find_all('a')):
            if idx == 0:
                player['source_player_code'] = a['href'].split('/')[-1].split('.php')[0]
                player['source_player_name'] = a.text
            elif idx == 1:
                cls = a.attrs['class'][-1]
                player['source_player_id'] = cls.split('-')[-1]

        # team_player_code
        sm = tds[1].find('small')
        if sm:
            player['source_team_code'] = sm.text.split(', ')[0]
        elif 'Defense' in player['source_player_name']:
            player['source_team_code'] = long_to_code(player['source_player_name'].split(' Defense')[0].strip())
        else:
            player['source_team_code'] = 'UNK'

        # fix for DST
        if 'defense' in player['source_player_code']:
            player['source_player_position'] = 'DST'
            player['source_team_code'] = long_to_code(player['source_player_name'].split(' Defense')[0].strip())

        if not player.get('source_team_code'):
            player['source_team_code'] = 'UNK'

        # get remaining stats
        player['adp'] = float(tds[-1].text)
        if not player.get('source_player_position'):
            player['source_player_position'] = \
                pos.get(player['source_player_code'], 'UNK')

        # position and posrk
        posrk = tds[2].text
        player['source_player_position'] = ''.join([s for s in posrk if not s.isdigit()])
        player['position_rank'] = int(''.join([s for s in posrk if s.isdigit()]))

        # get source player id
        player['source_player_id'] = pid.get(player['source_player_code'], 'UNK')

        # add to list
        players.append(player)

    return players


if __name__ == '__main__':
    pass