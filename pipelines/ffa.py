# pipelines/ffa.py
# manipulate projections from fantasyfootballanalytics.com

import logging

import feather
import pandas as pd

from pydfs_lineup_optimizer import *


logging.getLogger(__name__).addHandler(logging.NullHandler())


def _add_sals(r, d, interactive, defaultsal=1000):
    '''
    Adds salary based on player match

    Args:
        r(DataFrame): DataFrame row
        d(dict): salaries dict

    Returns:
        int

    '''
    ## add salaries
    k = '{}_{}'.format(r['full_name'], r['position'])
    match = d.get(k, defaultsal)
    if match > 0 or not interactive:
        sal = match
    else:
        sal = input('Add salary for {}: '.format(r['full_name']))
    return int(sal)


def _logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def _ffa_to_dk_teams(val):
    '''
    Converts team code used by ffa to dk team code

    Args:
        val(str): team name

    Returns:
        str

    '''
    conv = {'NEP': 'NE', 'NOS': 'NO', 'KCC': 'KC', 'JAC': 'JAX',
            'GBP': 'GB', 'SFO': 'SF', 'TBB': 'TB'}
    return conv.get(val, val)


def _namestrip(nm):
    '''
    Strips various characters out of name. Used for better matching.
    '''
    return nm.replace('Jr', '').replace('III', '').replace('IV', '') \
        .replace('II', '').replace('Fuller V', 'Fuller') \
        .replace("'", "").replace(".", "").replace(', ', '') \
        .replace(',', '').strip()


def _name_fix(r):
    '''
    Fixes name in dataframe row

    Args:
        r(DataFrame.row):

    Returns:
        str

    '''
    if r['position'] == 'DST':
        fn = r['last_name']
        ln = 'Defense'
        full_name = fn + ' ' + ln
    else:
        full_name = _namestrip(r['first_name'] + ' ' + r['last_name'])
    return full_name


def add_salaries(df, db, source, season_year, week, interactive=False):
    '''
    Adds salaries to player dataframe

    Args:
        df(DataFrame): players dataframe
        db(NFLPostgres): instance
        source(str): 'dk', 'fd', etc.
        season_year(int): NFL season
        week(int): NFL week

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
    return df


def clean_df(df):
    '''
    Cleans values in dataframe

    Args:
        df(DataFrame):

    Returns:
        DataFrame

    '''
    ## fix team
    df['team'] = df.apply(lambda x: _ffa_to_dk_teams(x['team']), axis=1)

    ## fix names
    df['full_name'] = df.apply(lambda x: _name_fix(x), axis=1)

    ## numeric types / replace NaN
    df['points'].fillna(0, inplace=True)

    return df


def _row_to_player(r):
    '''
    Converts row to Player
    '''
    try:
        return Player(
            player_id=r['id'],
            first_name=r['first_name'],
            last_name=r['last_name'],
            positions=[r['position']],
            team=r['team'],
            salary=r['salary'],
            fppg=r['points'])
    except Exception as e:
        logging.exception(r)
        logging.exception(e)


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
    qry = 'position == "{}" and points >= {}'
    dfs = [df.query(qry.format(pos, thresh.get(pos))) for pos in thresh]
    return pd.concat(dfs)


def lineups_to_df(lineups, fn=None):
    '''
    Converts list of lineups to dataframe

    Args:
        lineups(list): of LineupOptimizer
        fn(str): if want to save feather file

    Returns:
        pd.DataFrame

    '''
    selected_players = []
    exclude = ['positions', '_max_exposure', 'is_injured']
    for idx, l in enumerate(lineups):
        for p in l.lineup:
            pl = {k: v for k, v in vars(p).items() if k not in exclude}
            pl['position'] = p.positions[0]
            try:
                pl['deviated_fppg'] = round(p.deviated_fppg, 2)
            except:
                pass
            pl['simid'] = idx + 1
            selected_players.append(pl)

    df = pd.DataFrame(selected_players)
    if fn:
        feather.write_dataframe(df, fn)

    chosen = df.groupby('id')['id'].count().to_frame(name='n').reset_index()

    # summary dataframe
    cols = ['first_name', 'last_name', 'team', 'position', 'salary', 'fppg', 'n']
    summdf = df.join(chosen.set_index('id'), on='id') \
        .sort_values('n', ascending=False).groupby('id').head(1)
    return df, summdf[cols]


def optimizer_factory(source, players):
    '''
    Gets optimizer

    Args:
        source(str): name of dfs site
        players(list): of Player

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