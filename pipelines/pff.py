# pipelines/pff.py
# UNDER CONSTRUCTION


import feather
import pandas as pd


def _fpts(p):
    '''
    Calculates standard fantasy points

    Args:
        p(dict): fantasy player

    Returns:
        float

    '''
    fpts = 0
    fpts += p.get('pass_yds', 0.0) * .04
    fpts += p.get('pass_td', 0.0) * 4
    fpts += p.get('pass_int', 0.0) * -1
    fpts += p.get('fumbles', 0.0) * -2
    fpts += p.get('rec_yds', 0.0) * .1
    fpts += p.get('rec_td', 0.0) * 6
    fpts += p.get('rush_yds', 0.0) * .1
    fpts += p.get('rush_td', 0.0) * 6
    return fpts


def yearly_projections_table(vals, season_year, lua):
    '''
    Prepares dict for insertion in yearly_projections

    Args:
        vals(list): of dict
        season_year(int): 2018, etc.
        lua(str): timestamp string

    '''
    fix = []

    conv = {
     'projection_ts': 'projection_ts',
     'fumbles_lost': 'fumbles',
     'player_id': 'source_player_id',
     'player_name': 'source_player_name',
     'position': 'source_player_position',
     'pass_yds': 'pass_yds',
     'pass_td': 'pass_td',
     'pass_comp': 'pass_cmp',
     'pass_att': 'pass_att',
     'pass_sacked': 'sack',
     'pass_int': 'pass_int',
     'recv_receptions': 'rec',
     'recv_targets': 'rec_tgt',
     'recv_td': 'rec_td',
     'recv_yds': 'rec_yds',
     'rush_att': 'rush_att',
     'rush_td': 'rush_td',
     'rush_yds': 'rush_yds',
     'team_name': 'source_team_id',
    }

    for v in vals:
        f = {conv[k]:v for k,v in v.items() if k in conv}
        f['season_year'] = season_year
        f['projection_ts'] = lua
        f['source'] = 'pff'
        f['fantasy_points_std'] = _fpts(f)
        f['fantasy_points_hppr'] = f.get('fantasy_points_std',0) + (f.get('rec',0) * 0.5)
        f['fantasy_points_ppr'] = f.get('fantasy_points_std',0) + f.get('rec',0)
        fix.append(f)

    return fix


def get_pff_mfl_d(db):
    '''
    Dict of pff to mfl ids

    Args:
        db(NFLPostgres): instance

    Returns:
        dict

    '''
    q = """select pff_player_id as pid, mfl_player_id as mid
       from dfs.pff_mfl_xref"""
    return {p['pid']: p['mid'] for p in db.select_dict(q)}


def pff_to_df(proj):
    '''
    TODO: implement this
    Make sure filename matches pattern in the ffa-pydfs.R script

    '''
    df = pd.DataFrame(proj)
    for pos in ('QB', 'RB', 'WR', 'TE', 'DST'):
        fn = pos + '.feather'
        feather.write_dataframe(df.query('pos == "{}"'.format(pos), fn))
