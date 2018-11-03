# pipelines/pydfs.py
# transformations for pydfs-lineup-optimizer

import logging

import feather
import pandas as pd

import nfl.xref as nx
from pydfs_lineup_optimizer import get_optimizer, Player, Site, Sport, LineupOptimizer


logging.getLogger(__name__).addHandler(logging.NullHandler())


def df_to_players(df):
    '''
    Converts dataframe to list of Player

    Args:
        df(DataFrame):

    Returns:
        list: of Player

    '''
    return df.apply(lambda x: row_to_player(x), axis=1).tolist()


def lineups_to_df(lineups, fn=None):
    '''
    Converts list of pydfs lineups to dataframe

    Args:
        lineups(list): of LineupOptimizer
        fn(str): if want to save feather file

    Returns:
        tuple of pd.DataFrame

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
        for idx, p in enumerate(players):
            if 'DST' in players[idx].positions:
                players[idx].position = ('D',)
    elif source == 'yahoo':
        optimizer = get_optimizer(Site.YAHOO, Sport.FOOTBALL)
    elif source == 'fb':
        optimizer = get_optimizer(Site.FANBALL, Sport.FOOTBALL)
    else:
        raise ValueError('unknown source: {}'.format(source))
    optimizer.load_players(players)
    return optimizer


def row_to_player(r):
    '''
    Converts row to Player. Id is index so use 'name' property.

    Args:
        r(pd.DataFrame): row from dataframe

    Returns:
        Player

    '''
    try:
        return Player(
            player_id=r.name,
            first_name=r['first_name'],
            last_name=r['last_name'],
            positions=[r['position']],
            team=r['team'],
            salary=r['salary'],
            fppg=r['points'])
    except Exception as e:
        logging.exception(r)
        logging.exception(e)
        return None


if __name__ == '__main__':
    pass
