# nflfantasy/pipelines.py

import logging


class DK:

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
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


    @staticmethod
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


    @staticmethod
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


    @staticmethod
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


    @staticmethod
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

class FourForFour:

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
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


    @staticmethod
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


    @staticmethod
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


    @staticmethod
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


    @staticmethod
    def _namestrip(nm):
        '''
        Strips various characters out of name. Used for better matching.
        '''
        return nm.replace('Jr', '').replace('III', '').replace('IV', '') \
            .replace('II', '').replace('Fuller V', 'Fuller') \
            .replace("'", "").replace(".", "").replace(', ', '') \
            .replace(',', '').strip()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def df_to_players(df):
        '''
        Converts dataframe to list of Player

        Args:
            df(DataFrame):

        Returns:
            list: of Player

        '''
        return df.apply(lambda x: _row_to_player(x), axis=1).tolist()

    @staticmethod
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

    @staticmethod
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


class FantasyPros:

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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


class Fanball:

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
    def get_fb_salary(r, mfld, sald, interactive=False, defaultsal=2000):
        '''
        Adds salary based on player match

        Args:
            r(DataFrame): DataFrame row
            mfld(dict): dict of mfl_id: fb_player_id
            sald(dict): dict of fb_player_id: salary
            interactive(bool): do interactive matching, default False
            defaultsal(int): supply salary if no match, default 2000

        Returns:
            int

        '''
        # if already have salary, can skip
        ## otherwise add salaries
        if r['salary'] > 0:
            sal = r['salary']
        elif mfld.get(r['id']):
            fb_player_id = mfld.get(r['id'])
            sal = sald.get(fb_player_id, defaultsal)
        elif interactive:
            sal = input('Enter salary for {}: '.format(p['full_name']))
        else:
            sal = defaultsal
        return int(sal)

    @staticmethod
    def fb_salary_dict(db, season_year, week):
        '''
        Returns dict of id:salary

        Args:
            season_year(int):
            week(int):

        Returns:
            dict

        '''
        q = """SELECT source_player_id as id, salary as s
               FROM dfs.fbsal 
               WHERE season_year={} AND week={};"""
        return {p['id']: p['s'] for p in
                db.select_dict(q.format(season_year, week))}


class FantasyFootballAnalytics:

    def __init__(self):
        '''

        '''
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

    @staticmethod
    def _fix_fdpos(pos):
        if pos == 'DST':
            return 'D'
        else:
            return pos

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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



class ProFootballFocus:

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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

    @staticmethod
    def pff_to_df(proj):
        '''
        TODO: implement this
        Make sure filename matches pattern in the ffa-pydfs.R script

        '''
        df = pd.DataFrame(proj)
        for pos in ('QB', 'RB', 'WR', 'TE', 'DST'):
            fn = pos + '.feather'
            feather.write_dataframe(df.query('pos == "{}"'.format(pos), fn))


class PyDfs:

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
    def df_to_players(df):
        '''
        Converts dataframe to list of Player

        Args:
            df(DataFrame):

        Returns:
            list: of Player

        '''
        return df.apply(lambda x: row_to_player(x), axis=1).tolist()

    @staticmethod
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

    @staticmethod
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

    @staticmethod
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
