"""
draft_season_sim.py

simulates draft season
can be used to assess roster construction or
  marginal value of additional player at X position

"""

import logging
from multiprocessing import Pool, cpu_count
import random

import numpy as np
import pandas as pd

from nfl.utility import getdb


logging.getLogger(__name__).addHandler(logging.NullHandler())
position_slots = {'QB': [1,3], 'RB': [2,6],
                  'WR': [3,6], 'TE': [1,3]}


def six_team_league():
    """

    Returns:

    """
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



def get_data():
    '''
    Queries database for last 5 years of fantasy gamelogs

    Returns:
        DataFrame

    '''

    db = getdb('nfl')
    q = """SELECT * FROM fantasy.vw_fgl WHERE fpts IS NOT NULL"""
    df = pd.read_sql(q, db.conn)
    df.fpts = df.fpts.fillna(0)
    df['fpts'] = df['fpts'].astype(np.float16)
    df['year'] = df['year'].astype(np.int16)
    df['week'] = df['week'].astype(np.int8)
    df['posrk'] = df['posrk'].astype(np.int16)
    df['plyr'] = df.apply(lambda x: x['plyr'] + '_' + str(x['year']), axis=1)
    return df


def n_players(df, pos, n, distribution):
    '''
    Creates df of gamelogs from one season of two players

    Args:
        df(pandas.DataFrame): a pandas dataframe
        pos(str): 'qb', 'rb', 'wr', 'te'
        n(int): number of players
        distribution(str): 'tiered' or 'random'

    Returns:
        DataFrame: a pandas dataframe

    '''
    results = []
    pos = pos.lower()
    pos_distributions = {
        'qb':[0, 7, 14, 21, 28, 28],
        'rb':[0, 6, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192],
        'wr':[0, 6, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192],
        'te': [0, 7, 14, 21, 28, 28]
    }
    if pos not in pos_distributions:
        raise ValueError('invalid pos: {}'.format(pos))

    if distribution == 'tiered':
        pos_dist = pos_distributions.get(pos)
        for i in range(n):
            min = pos_dist[i]
            max = pos_dist[i+2]
            pool = df[(df['posrk'] >= min) & (df['posrk'] <= max) & (df['pos'] == pos.upper())]
            random_player = df.loc[random.choice(pool.index)]['plyr']
            results.append(pool[pool['plyr'] == random_player])

    elif distribution == 'random':
        pass

    else:
        raise ValueError('invalid distribution: {}'.format(distribution))

    return pd.concat(results)


def percentile(n):
    def percentile_(x):
        return np.percentile(x, n)
    percentile_.__name__ = 'percentile_%s' % n
    return percentile_


def position_season(df, pos, numstarters, numpos):
    '''
    Simulates bestball season for one fantasy position

    Args:
        df(DataFrame): weekly gamelogs
        pos(str): 'QB', 'RB', etc.

    '''
    posdf = df[df['pos'] == pos]
    tm = n_players(df, pos, numpos, 'tiered')
    plyr = list(tm.groupby('plyr').head(1)['plyr'])
    tm['tmrk'] = tm['plyr'].apply(lambda x: plyr.index(x) + 1)
    return tm.groupby('week'). \
        apply(lambda grp: grp.nlargest(numstarters, 'fpts')). \
        reset_index(drop=True)


def _weeks_used(df, pos, n):
    '''
    Simulates season to determine how many weeks a player gets used

    Args:
        df(DataFrame): with columns plyr, week, fpts, posrk
        pos(str): 'qb', 'rb', 'wr', 'te'
        n(int): number of iterations

    Returns:
        DataFrame

    '''
    # only need subset of the dataframe
    cols = ['plyr', 'week', 'pos', 'posrk', 'fpts']
    df = get_data()[cols]
    numstarters, numpos = position_slots[pos]
    results = []
    for i in range(n):
        seas = position_season(df, pos, numstarters, numpos)
        seas['iter'] = i
        results.append(seas)
    results = pd.concat(results)
    cnt = results.groupby(['iter', 'tmrk'])['tmrk'].count().unstack(fill_value=0).stack()
    return pos, cnt.groupby('tmrk').aggregate(
        [np.sum, np.min, percentile(25), np.mean, np.median, percentile(75), np.max])

def weeks_used(df, pos, n):
        '''
        Simulates season to determine how many weeks a player gets used

        Args:
            df(DataFrame): with columns plyr, week, fpts, posrk
            pos(str): 'qb', 'rb', 'wr', 'te'
            n(int): number of iterations

        Returns:
            DataFrame

        '''
        with Pool(cpu_count()) as p:
            positions = ['QB', 'RB', 'WR', 'TE']
            results = p.starmap(_weeks_used, tuple(zip([df] * len(positions),
                                                       positions,
                                                       [n] * len(positions))))
            for result in results:
                print(result[0])
                print()
                print(result[1])
                print()


if __name__ == '__main__':
    pass