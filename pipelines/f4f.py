# pipelines/ffa.py
# manipulate projections from fantasyfootballanalytics.com

import logging
from uuid import uuid4

import pandas as pd

from pydfs_lineup_optimizer import *


logging.getLogger(__name__).addHandler(logging.NullHandler())


def _add_sals(r, d, interactive=True):
    '''
    Adds salary based on player match

    Args:
        r(DataFrame.row): DataFrame row
        d(dict): salaries dict

    Returns:
        int

    '''
    ## add salaries
    k = '{}_{}'.format(r['player'], r['pos'])
    match = d.get(k)
    if match:
        sal = match
    elif interactive:
        sal = int(input('Add salary for {}: '.format(r['player'])))
    else:
        sal = 10000
    return sal


def _dummy_dst(rows, dst_salary=3000, ffpts=5.0):
    '''
    Creates dummy DST for 4 for 4 projections

    Args:
        rows(DataFrame): the dataframe to randomize
        dst_salary(int): dummy price for DST
        ffpts(float): fantasy points

    Returns:
        df

    '''
    rows['salary'] = dst_salary
    rows['ffpts'] = ffpts
    rows['pid'] = rows['pid'].apply(lambda x: str(uuid4())[0:8])
    rows['first_name'] = 'Dummy'
    rows['last_name'] = 'Defense'
    rows['team'] = 'DMY'
    rows['player'] = rows['first_name'] + ' ' + rows['last_name']
    rows['pos'] = 'DST'
    return rows


def _f4f_to_dk_teams(val):
    '''
    Converts team code used by 4 for 4 to dk team code

    Args:
        val(str): team name

    Returns:
        str

    '''
    conv = {'NEP': 'NE', 'NOS': 'NO', 'KCC': 'KC', 'JAC': 'JAX',
            'GBP': 'GB', 'SFO': 'SF', 'TBB': 'TB'}
    return conv.get(val, val)


def _name_fix(df):
    '''
    Fixes name in dataframe

    Args:
        df(DataFrame):

    Returns:
        str

    '''
    # 4 for 4 has player column with no defense
    df['player'] = df['player'].apply(lambda x: _namestrip(x))
    df[['first_name', 'last_name']] = df['player'].str.split(' ', expand=True)
    return df


def _namestrip(nm):
    '''
    Strips various characters out of name. Used for better matching.
    '''
    return nm.replace('Jr', '').replace('III', '').replace('IV', '') \
        .replace('II', '').replace('Fuller V', 'Fuller') \
        .replace("'", "").replace(".", "").replace(', ', '') \
        .replace(',', '').strip()



def _row_to_player(r):
    '''
    Converts row to Player
    '''
    return Player(
        player_id=r['pid'],
        first_name=r['first_name'],
        last_name=r['last_name'],
        positions=[r['pos']],
        team=r['team'],
        salary=int(r['salary']),
        fppg=float(r['ffpts']))


def add_dst(df):
    '''
    Adds dummy DST teams to dataframe

    Args:
        df(DataFrame):

    Returns:
        DataFrame

    '''
    dst = _dummy_dst(df[0:10].copy())
    return pd.concat([df, dst], ignore_index=True, sort=False)


def add_salaries(df, db, source, season_year, week, interactive=True):
    '''
    Adds salaries to player dataframe

    Args:
        df(DataFrame): players dataframe
        db(NFLPostgres): instance
        source(str): 'dk', 'fd', etc.
        season_year(int): NFL season
        week(int): NFL week
        interactive(bool): prompt for missing salaries?

    Returns:
        DataFrame

    '''
    q = """SELECT
              CASE WHEN dfs_position = 'DST' THEN 
                CONCAT(source_player_name, 'Defense') 
                ELSE source_player_name END 
                AS source_player_name,
              dfs_position,
              salary
           FROM dfs.fn_{}sal_sws({}, {})"""
    sals = db.select_dict(q.format(source, season_year, week))
    sals_d = {'{}_{}'.format(_namestrip(p['source_player_name']),
                             p['dfs_position']): p['salary']
              for p in sals}
    df['salary'] = df.apply(lambda x: _add_sals(x, sals_d, interactive), axis=1)
    df['salary'] = df['salary'].astype(int)
    return df


def clean_df(df):
    '''
    Cleans values in dataframe

    Args:
        df(DataFrame):

    Returns:
        DataFrame

    '''
    ## change column names
    ## fix team
    ## fix names
    ## numeric types / replace NaN
    df.columns = df.columns.str.lower()
    df['team'] = df['team'].apply(lambda x: _f4f_to_dk_teams(x))
    df = _name_fix(df)
    df['ffpts'].fillna(0, inplace=True)
    return df


def df_to_players(df):
    '''
    Converts dataframe to list of Player

    Args:
        df(DataFrame):

    Returns:
        list: of Player

    '''
    return df.apply(lambda x: _row_to_player(x), axis=1).tolist()


def filter_players(df, thresh=None):
    '''
    Applies positional thresholds

    Args:
        df(DataFrame): df to filter

    Returns:
        DataFrame: filtered by positional thresholds

    '''
    if not thresh:
        thresh = {'QB': 14.0, 'WR': 9.0, 'RB': 9.0, 'TE': 7.0, 'DST': 3.0}
    qry = 'pos == "{}" and ffpts >= {}'
    dfs = [df.query(qry.format(pos, thresh.get(pos))) for pos in thresh]
    return pd.concat(dfs)


def optimizer_factory(source, players):
    '''
    Gets optimizer

    Args:
        source(str): name of dfs site
        players(df):

    Returns:
        LineupOptimizer

    '''
    if source == 'dk':
        optimizer = get_optimizer(Site.DRAFTKINGS, Sport.FOOTBALL)
    elif source == 'fd':
        optimizer = get_optimizer(Site.FANDUEL, Sport.FOOTBALL)
    elif source == 'yahoo':
        optimizer = get_optimizer(Site.YAHOO, Sport.FOOTBALL)
    else:
        raise ValueError('unknown source: {}'.format(source))
    optimizer.load_players(players)
    return optimizer


if __name__ == '__main__':
    pass