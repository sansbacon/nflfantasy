# -*- coding: utf-8 -*-

import logging
import random
import sys
import unittest

import pandas as pd

from pydfs_lineup_optimizer import Player
import nflfantasy.pipelines as pl
from nfl.utility import rand_dictitem


class NFLPipelines_test(unittest.TestCase):
    '''
    '''

    def setUp(self):
        self.dk = pl.DK()
        self.fff = pl.FourForFour()

    def test_fff_add_sals(self):
        '''
        tests FourForFour._add_sals

        '''
        players = [{'player': 'Joe Smith', 'pos': 'QB'},
                   {'player': 'Joe Smythe', 'pos': 'RB'}]
        df = pd.DataFrame(players)
        d = {'Joe Smith_QB': 5400}
        sal = self.fff._add_sals(df.iloc[0], d)
        self.assertEqual(sal, 5400)
        sal = self.fff._add_sals(df.iloc[1], d)
        self.assertEqual(sal, 10000)

    def test_fff_dummy_dst(self):
        '''
        tests FourForFour._dummy_dst

        '''
        teams = pd.DataFrame([{'pid': 12345, 'pos': 'Def', 'sal': 3200},
                              {'pid': 54321, 'pos': 'Def', 'sal': 3600}])

        # test default settings
        dummy = self.fff._dummy_dst(rows=teams)
        row = dummy.sample(1)
        self.assertEqual(3000, row['salary'].iloc[0])
        self.assertEqual(5.0, row['ffpts'].iloc[0])

        # test custom values
        sal = 6000
        ffpts = 1.0
        dummy = self.fff._dummy_dst(rows=teams, dst_salary=sal, ffpts=ffpts)
        row = dummy.sample(1)
        self.assertEqual(sal, row['salary'].iloc[0])
        self.assertEqual(ffpts, row['ffpts'].iloc[0])

    def test_f4f_to_dk_teams(self):
        '''
        Tests FourForFour._f4f_to_dk_teams

        '''
        conv = {'NEP': 'NE', 'NOS': 'NO', 'KCC': 'KC', 'JAC': 'JAX',
                'GBP': 'GB', 'SFO': 'SF', 'TBB': 'TB'}
        k, v = rand_dictitem(conv)
        team = self.fff._f4f_to_dk_teams(k)
        self.assertEqual(team, v)

    def test_f4f_name_fix(self):
        '''
        Tests FourForFour._name_fix

        '''
        players = [{'player': 'Joe Smith Jr.', 'pos': 'QB'},
                   {'player': 'Joe Smythe III', 'pos': 'RB'}]
        df = pd.DataFrame(players)
        df = self.fff._name_fix(df)
        self.assertEqual(df.iloc[0]['player'], 'Joe Smith')
        self.assertEqual(df.iloc[1]['player'], 'Joe Smythe')

    def test_f4f_row_to_player(self):
            '''
            Tests FourForFour._name_fix

            '''
            teams = pd.DataFrame([{'pid': 12345, 'pos': 'Def', 'sal': 3200},
                                  {'pid': 54321, 'pos': 'Def', 'sal': 3600}])
            dummy = self.fff._dummy_dst(rows=teams)
            row = dummy.sample(1).iloc[0]
            player = self.fff._row_to_player(row)
            self.assertIsInstance(player, Player)
            self.assertEqual(player.salary, row['salary'])

    # I'm not sure how to test these
    # Maybe the best I can do is test the internals they rely on?
    # Otherwise need fixed data file
    def test_fff_add_dst(self):
        pass

        # need sample dataframe for this to work
        '''
            Adds dummy DST teams to dataframe

            Args:
                df(DataFrame):

            Returns:
                DataFrame

        '''

    def test_fff_add_salaries(self):

        pass
        #(df, db, source, season_year, week, interactive=True):
        '''
        Adds salaries to player dataframe

        Args:
            df(DataFrame): players dataframe
            db(NFLPostgres): instance
            source(str): 'dk', 'fd', etc.
            season_year(int): NFL season
            week(int): NFL week
            interactive(bool): prompt for missing salaries?
        '''

    def test_fff_clean_df(self):
        # (df):
        '''
        Cleans values in dataframe

        Args:
            df(DataFrame):

        Returns:
            DataFrame

        '''
        pass

    def test_fff_df_to_players(df):
        '''
        Converts dataframe to list of Player

        Args:
            df(DataFrame):

        Returns:
            list: of Player

        '''
        pass

    def test_fff_filter_players(self):
        #(df, thresh=None):
        '''
        Applies positional thresholds

        Args:
            df(DataFrame): df to filter

        Returns:
            DataFrame: filtered by positional thresholds

        '''
        pass

    def test_fff_optimizer_factory(self):
        #(source, players):
        '''
            Gets optimizer

            Args:
            source(str): name of dfs site
            players(df):

            Returns:
            LineupOptimizer

        '''
        pass


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
