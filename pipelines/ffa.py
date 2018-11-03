# pipelines/ffa.py
# manipulate projections from fantasyfootballanalytics.com

import logging

import pandas as pd

import nfl.xref as nx
from playermatcher.name import namestrip


logging.getLogger(__name__).addHandler(logging.NullHandler())

FFACOLS = {
    'qb': ['data_src', 'id', 'src_id', 'player', 'team', 'pos', 'status', 'wk_8_opp',
           'wk_8_status_et', 'pass_comp', 'pass_att', 'pass_yds', 'pass_tds',
           'pass_int', 'rush_att', 'rush_yds', 'rush_tds', 'rec', 'rec_yds',
           'rec_tds', 'site_pts', 'chg', 'opp', 'number', 'tm', 'pass_09_tds',
           'pass_1019_tds', 'pass_2029_tds', 'pass_3039_tds', 'pass_4049_tds',
           'pass_50_tds', 'sacks', 'fumbles_lost', 'opp1', 'z', 'note',
           'status_game_opp', 'z1', 'forecast', 'owner', 'games', 'bye',
           'fantasy_percent_owned', 'rankings_proj', 'rankings_actual',
           'pass_inc', 'passing_pick_six', 'pass_1st', 'pass_40_yds', 'rush_1st',
           'rush_40_yds', 'rec_tgt', 'rec_1st', 'rec_40_yds', 'ret_yds', 'ret_tds',
           'two_pts', 'fumbles_total', 'na', 'player.1', 'site_ci_low', 'site_ci_high',
           'opp_team', 'opp_rank', 'ranks_ovr', 'ranks_pos', 'fan_duel_fp',
           'fan_duel_cost', 'fan_duel_value', 'draft_kings_fp',
           'draft_kings_cost', 'draft_kings_value', 'yahoo_fp', 'yahoo_cost',
           'yahoo_value', 'week_8_opp', 'week_8_f_pts', 'pass_comp_pct', 'pass_rate',
           'z2', 'z3', 'z4', 'availability_percent_own', 'esbid', 'gsis_player_id',
           'team_abbr', 'season_pts', 'site_season_pts', 'week_pts'],

    'rb': ['data_src', 'id', 'src_id', 'player', 'team', 'pos', 'status',
           'wk_8_opp', 'wk_8_status_et', 'pass_comp', 'pass_att',
           'pass_yds', 'pass_tds', 'pass_int', 'rush_att', 'rush_yds',
           'rush_tds', 'rec', 'rec_yds', 'rec_tds', 'site_pts', 'chg',
           'opp', 'number', 'tm', 'rush_09_tds', 'rush_1019_tds',
           'rush_2029_tds', 'rush_3039_tds', 'rush_4049_tds',
           'rush_50_tds', 'rush_50_yds', 'rush_100_yds', 'punt_ret_yds',
           'kick_ret_yds', 'fumbles_lost', 'opp1', 'z', 'note',
           'status_game_opp', 'z1', 'forecast', 'owner', 'games',
           'bye', 'fantasy_percent_owned', 'rankings_proj',
           'rankings_actual', 'pass_inc', 'passing_pick_six',
           'sacks', 'pass_1st', 'pass_40_yds', 'rush_1st',
           'rush_40_yds', 'rec_tgt', 'rec_1st', 'rec_40_yds',
           'ret_yds', 'ret_tds', 'two_pts', 'fumbles_total',
           'na', 'player.1', 'site_ci_low', 'site_ci_high',
           'opp_team', 'opp_rank', 'ranks_ovr', 'ranks_pos',
           'fan_duel_fp', 'fan_duel_cost', 'fan_duel_value',
           'draft_kings_fp', 'draft_kings_cost', 'draft_kings_value',
           'yahoo_fp', 'yahoo_cost', 'yahoo_value', 'week_8_opp',
           'week_8_f_pts', 'z2', 'z3', 'misc_td', 'misc_yd', 'z4',
           'z5', 'availability_percent_own', 'esbid', 'gsis_player_id',
           'team_abbr', 'season_pts', 'site_season_pts', 'week_pts',
           'tack', 'ast', 'int', 'frc_fum', 'fum_rec', 'pass_def'],

    'wr': ['data_src', 'id', 'src_id', 'player', 'team', 'pos',
           'status', 'wk_8_opp', 'wk_8_status_et', 'pass_comp',
           'pass_att', 'pass_yds', 'pass_tds', 'pass_int', 'rush_att',
           'rush_yds', 'rush_tds', 'rec', 'rec_yds', 'rec_tds', 'site_pts',
           'chg', 'opp', 'number', 'tm', 'rec_tgt', 'rec_rz_tgt',
           'rec_09_tds', 'rec_1019_tds', 'rec_2029_tds', 'rec_3039_tds',
           'rec_4049_tds', 'rec_50_tds', 'punt_ret_yds', 'kick_ret_yds',
           'fumbles_lost', 'opp1', 'z', 'note', 'status_game_opp', 'z1',
           'forecast', 'owner', 'games', 'bye', 'fantasy_percent_owned',
           'rankings_proj', 'rankings_actual', 'pass_inc',
           'passing_pick_six', 'sacks', 'pass_1st', 'pass_40_yds',
           'rush_1st', 'rush_40_yds', 'rec_1st', 'rec_40_yds',
           'ret_yds', 'ret_tds', 'two_pts', 'fumbles_total', 'na',
           'player.1', 'site_ci_low', 'site_ci_high', 'opp_team',
           'opp_rank', 'ranks_ovr', 'ranks_pos', 'fan_duel_fp',
           'fan_duel_cost', 'fan_duel_value', 'draft_kings_fp',
           'draft_kings_cost', 'draft_kings_value', 'yahoo_fp',
           'yahoo_cost', 'yahoo_value', 'week_8_opp', 'week_8_f_pts',
           'z2', 'z3', 'misc_td', 'misc_yd', 'z4', 'z5',
           'availability_percent_own', 'esbid', 'gsis_player_id',
           'team_abbr', 'season_pts', 'site_season_pts', 'week_pts'],

    'te': ['data_src', 'id', 'src_id', 'player', 'team', 'pos',
           'status', 'wk_8_opp', 'wk_8_status_et', 'pass_comp',
           'pass_att', 'pass_yds', 'pass_tds', 'pass_int', 'rush_att',
           'rush_yds', 'rush_tds', 'rec', 'rec_yds', 'rec_tds', 'site_pts',
           'chg', 'opp', 'number', 'tm', 'rec_tgt', 'rec_rz_tgt',
           'rec_09_tds', 'rec_1019_tds', 'rec_2029_tds', 'rec_3039_tds',
           'rec_4049_tds', 'rec_50_tds', 'punt_ret_yds', 'kick_ret_yds',
           'fumbles_lost', 'opp1', 'z', 'note', 'status_game_opp', 'z1',
           'forecast', 'owner', 'games', 'bye', 'fantasy_percent_owned',
           'rankings_proj', 'rankings_actual', 'pass_inc',
           'passing_pick_six', 'sacks', 'pass_1st', 'pass_40_yds',
           'rush_1st', 'rush_40_yds', 'rec_1st', 'rec_40_yds',
           'ret_yds', 'ret_tds', 'two_pts', 'fumbles_total', 'na',
           'player.1', 'site_ci_low', 'site_ci_high', 'opp_team',
           'opp_rank', 'ranks_ovr', 'ranks_pos', 'fan_duel_fp',
           'fan_duel_cost', 'fan_duel_value', 'draft_kings_fp',
           'draft_kings_cost', 'draft_kings_value', 'yahoo_fp',
           'yahoo_cost', 'yahoo_value', 'week_8_opp', 'week_8_f_pts',
           'z2', 'z3', 'misc_td', 'misc_yd', 'z4', 'z5',
           'availability_percent_own', 'esbid', 'gsis_player_id',
           'team_abbr', 'season_pts', 'site_season_pts', 'week_pts'],

    'dst': ['data_src', 'id', 'src_id', 'player',
            'pos', 'wk_8_opp', 'wk_8_status_et',
            'dst_tackle', 'dst_sacks', 'dst_fum_force',
            'dst_fum_rec', 'dst_int', 'dst_int_tds', 'dst_ret_tds',
            'site_pts', 'number', 'tm', 'opp', 'dst_yds_allowed',
            'dst_pts_allowed', 'dst_td', 'dst_safety', 'z', 'note',
            'team', 'status_game_opp', 'z1', 'owner', 'games', 'bye',
            'fantasy_percent_owned', 'rankings_proj', 'rankings_actual',
            'dst_tfl', 'dst_blk', 'dst_4_down', 'dst_3_out', 'dst_ret_yds',
            'na', 'player.1', 'site_ci_low', 'site_ci_high', 'opp_team',
            'opp_rank', 'ranks_pos', 'fan_duel_fp', 'fan_duel_cost',
            'fan_duel_value', 'draft_kings_fp', 'draft_kings_cost',
            'draft_kings_value', 'yahoo_fp', 'yahoo_cost', 'yahoo_value',
            'team_abbr', 'season_pts', 'site_season_pts', 'week_pts', 'dst_ret_td']}

PFFKEY_TO_FFAKEY = {
    'qb': {
        'fumbles': 'fumbles_total',
        'fumbles_lost': 'fumbles_lost',
        'two_pt': 'two_pts',
        'fantasy_points': 'site_pts',
        'player_id': 'src_id',
        'player_name': 'player',
        'position': 'pos',
        'team_name': 'tm',
        'pass_att': 'pass_att',
        'pass_comp': 'pass_comp',
        'pass_int': 'pass_int',
        'pass_sacked': 'sacks',
        'pass_td': 'pass_tds',
        'pass_yds': 'pass_yds',
        'rush_att': 'rush_att',
        'rush_td': 'rush_tds',
        'rush_yds': 'rush_yds'},

    'rb': {
        'fumbles': 'fumbles_total',
        'fumbles_lost': 'fumbles_lost',
        'recv_receptions': 'rec',
        'recv_targets': 'rec_tgt',
        'recv_td': 'rec_tds',
        'recv_yds': 'rec_yds',
        'two_pt': 'two_pts',
        'fantasy_points': 'site_pts',
        'player_id': 'src_id',
        'player_name': 'player',
        'position': 'pos',
        'team_name': 'tm',
        'rush_att': 'rush_att',
        'rush_td': 'rush_tds',
        'rush_yds': 'rush_yds'},

    'wr': {
        'fumbles': 'fumbles_total',
        'fumbles_lost': 'fumbles_lost',
        'recv_receptions': 'rec',
        'recv_targets': 'rec_tgt',
        'recv_td': 'rec_tds',
        'recv_yds': 'rec_yds',
        'two_pt': 'two_pts',
        'fantasy_points': 'site_pts',
        'player_id': 'src_id',
        'player_name': 'player',
        'position': 'pos',
        'team_name': 'tm',
        'rush_att': 'rush_att',
        'rush_td': 'rush_tds',
        'rush_yds': 'rush_yds'},

    'te': {
        'fumbles': 'fumbles_total',
        'fumbles_lost': 'fumbles_lost',
        'recv_receptions': 'rec',
        'recv_targets': 'rec_tgt',
        'recv_td': 'rec_tds',
        'recv_yds': 'rec_yds',
        'two_pt': 'two_pts',
        'fantasy_points': 'site_pts',
        'player_id': 'src_id',
        'player_name': 'player',
        'position': 'pos',
        'team_name': 'tm'},

    'dst': {
        'dst_fumbles_forced': 'dst_fum_force',
        'dst_fumbles_recovered': 'dst_fum_rec',
        'dst_int': 'dst_int',
        'dst_return_td': 'dst_ret_tds',
        'dst_sacks': 'dst_sacks',
        'dst_safeties': 'dst_safety',
        'dst_td': 'dst_td',
        'fantasy_points': 'site_pts',
        'player_id': 'src_id',
        'player_name': 'player',
        'position': 'pos',
        'team_name': 'tm'}
}


def _fix_fdpos(pos):
    if pos == 'DST':
        return 'D'
    else:
        return pos


def _name_fix(r):
    '''
    Adds first + last name or city + defense for DST

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
        full_name = namestrip(r['first_name'] + ' ' + r['last_name'])
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
    mfldict = _mfld(db, season_year, week, source)
    keydict = _keyd(db, season_year, week, source)
    df['id'] = df['id'].astype(int)
    if not 'salary' in df.columns:
        df['salary'] = 0
    if source == 'fb':
        fb = nx.Fanball(db)
        mfl_fb_d = nx.get_mfld()
        sald = _fb_salary_dict(db, season_year, week)
        df['salary'] = df.apply(lambda x: _add_fbsals(x, mfld=mfl_fb_d, sald=sald,
                                                      interactive=interactive), axis=1)
    else:
        df['salary'] = df.apply(lambda x: _add_sals(x, mfld=mfldict, sald=sald,
                                                    interactive=interactive), axis=1)
    return df


def clean_projections(df, source):
    '''
    Cleans values in projections dataframe

    Args:
        df(DataFrame):
        source(str): 'dk', 'fd', etc.

    Returns:
        DataFrame

    '''
    ## fix team
    logging.info('clean_df: starting fix team')
    if source == 'dk':
        df['team'] = df.apply(lambda x: _ffa_to_dk_teams(x['team']), axis=1)

    ## fix names
    logging.info('clean_df: starting fix names')
    df['full_name'] = df.apply(lambda x: _name_fix(x), axis=1)

    ## numeric types / replace NaN
    logging.info('clean_df: starting fix numeric types')
    for col in ['points', 'floor', 'ceiling', 'pos_ecr', 'risk']:
        if col in df.columns:
            df[col].fillna(0, inplace=True)
    df['id'] = df['id'].astype(int)

    # return clean df
    return df


def ffa_to_dk_teams(val):
    '''
    Converts team code used by ffa to dk team code

    Args:
        val(str): team name

    Returns:
        str

    '''
    conv = {'NEP': 'NE', 'NOS': 'NO', 'KCC': 'KC', 'JAC': 'JAX',
            'GBP': 'GB', 'SFO': 'SF', 'TBB': 'TB'}
    logging.debug('converting team {}'.format(val))
    return conv.get(val, val)


def filter_players(df, thresh=None):
    '''
    Applies projection thresholds to positions

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


def pff_to_ffa(pff_players, pff_mfl_d):
    '''
    Converts PFF player to ffanalytics format

    Args:
        pff_players(list): of dict
        pff_mfl_d(dict): xref pff to mfl ids

    Returns:
        list: of dict

    '''
    ffa_players = []
    for p in pff_players:
        # initialize with none; can change if available
        pos = p.get('position').lower()
        if FFACOLS.get(pos):
            ffadict = {c:None for c in FFACOLS.get(pos)}
            ffadict['data_src'] = 'PFF'
            for pffkey, ffakey in PFFKEY_TO_FFAKEY.get(pos).items():
                ffadict[ffakey] = p.get(pffkey, None)
            # add player id
            ffadict['id'] = pff_mfl_d.get(p['player_id'])
            # now deal with pts allowed if DST
            if pos == 'dst':
                pts_allowed = [k for k,v in p.items() if
                               'dst_pts' in k and v == 1.0]
                if pts_allowed:
                    ffadict['dst_pts_allowed'] = pts_allowed[0].split('_')[-1]
            ffa_players.append(ffadict)
    return ffa_players


if __name__ == '__main__':
    pass
