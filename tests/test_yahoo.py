import logging

from nflfantasy.scrapers.yahoo import YahooFantasyScraper


import unittest


class Yahoo_test(unittest.TestCase):

    def setUp(self):
        '''
        Setup scraper and parser

        '''
        logging.basicConfig(level=logging.INFO)
        self.scraper = YahooFantasyScraper('auth.json')

    def test_players(self):
        '''
        Test all subresources

        '''
        g = self.scraper.players(league_id=74419)
        logging.info(g)
        self.assertIsNotNone(g.get('fantasy_content'))


    """
    @property
    def league_id(self):
        return random.choice([8397, 53830, 50755])

    def league_keys(self, n):
        return random.sample(['375.l.8397', '375.l.53830', '375.l.50755'], n)

    def player_keys(self, n):
        return random.sample(['375.p.3930', '375.p.4840', '375.p.4912', '375.p.4244'], n)

    def team_keys(self, n):
        return random.sample(['375.l.8397.t.8', '375.l.53830.t.9', '375.l.50755.t.1'], n)

    @property
    def transaction_key(self):
        return random.choice(['375.l.53830.tr.15', '375.l.53830.tr.14', '375.l.50755.tr.1', '375.l.50755.tr.2'])

    @unittest.skip('skip test_game')
    def test_game(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.game_subresources:
            if subr == 'leagues':
                g = self.scraper.game(subresource=subr, keys=self.league_keys(1))
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))
            elif subr == 'players':
                g = self.scraper.game(subresource=subr, keys=self.player_keys(1))
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))
            else:
                g = self.scraper.game(subresource=subr)
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_games')
    def test_games(self):
        '''
        Test all games subresources and filters

        '''
        # loop through subresources
        for subr in self.scraper.games_subresources:
            logging.info('subresources: {}'.format(subr))
            if subr == 'leagues':
                g = self.scraper.games(subresource=subr, keys=self.league_keys(1))
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))
            elif subr == 'players':
                g = self.scraper.games(subresource=subr, keys=self.player_keys(1))
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))
            elif subr == 'teams':
                continue
            else:
                g = self.scraper.games(subresource=subr)
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))

        # loop through filters
        filts = {'is_available': {'is_available': 1}, 'game_types': {'game_types': 'full'},
                 'game_codes': {'game_codes': [375]}, 'seasons': {'seasons': [2017]}}
        for filter in self.scraper.games_filters:
            logging.info('filters: {}'.format(filter))
            g = self.scraper.games(filters=filts[filter])
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_league')
    def test_league(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.league_subresources:
            g = self.scraper.league(league_id=self.league_id, subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_leagues')
    def test_leagues(self):
        '''
        Test all leagues subresources and filters
        
        '''
        # loop through subresources
        # test with and without league keys
        for subr in self.scraper.leagues_subresources:
            logging.info('subresources with league keys: {}'.format(subr))
            g = self.scraper.leagues(subresource=subr, league_keys=self.league_keys(1))
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_player')
    def test_player(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.player_subresources:
            g = self.scraper.player(player_key=self.player_keys(1)[0], subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_players')
    def test_players(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.players_subresources:
            # league
            g = self.scraper.players(league_id=self.league_id, subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

            # leagues
            g = self.scraper.players(league_ids=[self.league_id, self.league_id], subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

            # team
            g = self.scraper.players(team_key=self.team_keys(1)[0], subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

            # teams
            g = self.scraper.players(team_keys=self.team_keys(2), subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

            # players
            g = self.scraper.players(player_keys=self.player_keys(2), subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

        filts = {'position': {'position': random.choice(['PG', 'SG', 'SF', 'PF', 'C'])},
                 'status': {'status': random.choice(['A', 'FA', 'W', 'T', 'K'])},
                 'search': {'search': random.choice(['smith', 'williams', 'jones'])},
                 'sort': {'sort': '60'},
                 'sort_type': {'sort_type': random.choice(['season', 'lastmonth', 'lastweek'])},
                 'sort_season': {'sort_season': self.scraper.yahoo_season},
                 'sort_date': {'sort_date': '2018-01-15'},
                 'start': {'start': random.randint(0,40)},
                 'count': {'count': random.randint(1,10)}}

        for filt in self.scraper.players_filters:
            g = self.scraper.players(self.league_id, filters=filts[filt])
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_roster')
    def test_roster(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.roster_subresources:
            tk = self.team_keys(1)
            g = self.scraper.roster(team_key=tk[0], subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

        tk = self.team_keys(1)
        g = self.scraper.roster(team_key=tk[0], subresource=subr, roster_date=self.roster_date)
        logging.info(g)
        self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_team')
    def test_team(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.team_subresources:
            tk = self.team_keys(1)
            g = self.scraper.team(team_key=tk[0], subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_teams')
    def test_teams(self):
        '''
        Test all subresources and filters

        '''
        for subr in self.scraper.teams_subresources:
            g = self.scraper.teams(league_id=self.league_id, subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

            g = self.scraper.teams(team_keys=self.team_keys(2), subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

            g = self.scraper.teams(my_team=True, subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_transaction')
    def test_transaction(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.transaction_subresources:
            g = self.scraper.transaction(transaction_key=self.transaction_key, subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_transactions')
    def test_transactions(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.transactions_subresources:
            g = self.scraper.transactions(league_id=self.league_id, subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

        # loop through filters
        filts = {'type': {'type': 'add'}, 'types': {'types': 'add,trade'},
                 'team_key': {'team_key': self.team_keys(1)[0]}, 'count': {'count': random.randint(1,5)}}
        for filter in self.scraper.transactions_filters:
            logging.info('filters: {}'.format(filter))
            if filter == 'team_key':
                league_id = filts['team_key']['team_key'].split('.')[2]
                g = self.scraper.transactions(league_id=league_id, filters=filts['team_key'])
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))
            else:
                g = self.scraper.transactions(league_id=self.league_id, filters=filts[filter])
                logging.info(g)
                self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_user')
    def test_user(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.user_subresources:
            g = self.scraper.user(subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_users')
    def test_users(self):
        '''
        Test all subresources

        '''
        for subr in self.scraper.users_subresources:
            g = self.scraper.users(subresource=subr)
            logging.info(g)
            self.assertIsNotNone(g.get('fantasy_content'))

    @unittest.skip('skip test_parse_leagues')
    def test_parse_leagues(self):
        '''
        parser.league
        
        '''
        self.scraper.response_format ='xml'
        content = self.scraper.leagues(league_keys=self.league_keys(2))
        leagues = self.parser.leagues(content=content)
        logging.info(leagues)
        self.assertIsNotNone(leagues)

    def test_parse_game(self):
        '''
        parser.game

        '''
        self.scraper.response_format = 'xml'
        content = self.scraper.game()
        games = self.parser.game(content=content)
        logging.info(games)
        self.assertIsNotNone(games)

        # why is stat_categories a blank line?
        content = self.scraper.game(subresource='stat_categories')
        games = self.parser.game(content=content)
        logging.info(games)
        self.assertIsNotNone(games)

        content = self.scraper.game(subresource='position_types')
        games = self.parser.game(content=content)
        logging.info(games)
        self.assertIsNotNone(games)

    """


if __name__=='__main__':
    unittest.main()
