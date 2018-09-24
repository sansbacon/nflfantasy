import logging
import os
from pathlib import Path
import random
import sys
import unittest

import pandas as pd
from pydfs_lineup_optimizer import LineupOptimizer

from nfl.utility import getdb
from nflfantasy.pipelines import f4f


class F4F_pipeline_test(unittest.TestCase):
    '''
    Tests pipeline functions

    '''
    _df = None

    def setUp(self):
        self.db = getdb('nfl')
        self.season_year = 2018
        self.week = 3
        self.source = 'dk'
        self.dst_salary = 3000
        sys._called_from_test = True

    def tearDown(self):
        del sys._called_from_test

    @property
    def col(self):
        return random.choice(['ffpts', 'player', 'pid'])

    @property
    def df(self):
        if not self._df:
            self._df = pd.read_csv(self.projcsv)
            self._df.columns = self._df.columns.str.lower()
        return self._df

    @property
    def fn(self):
        return '{}_w{}_f4f-{}proj.csv'.format(self.season_year,
                                              self.week, self.source)
    @property
    def projcsv(self):
        return self.projdir / '4for4' / self.fn

    @property
    def projdir(self):
        return self.scrdir / 'data'

    @property
    def rows(self):
        return self.df[0:10].copy()

    @property
    def scrdir(self):
        return Path(os.path.dirname(os.path.realpath(__file__)))

    def test_load(self):
        df = self.df
        col = self.col
        self.assertTrue(col in df.columns, 'Should have {} column'.format(col))

    def test_dummy_dst(self):
        rows = f4f._dummy_dst(self.rows)
        self.assertEqual(10, len(rows), 'Rows should be the same')

    def test_name_fix(self):
        df = self.df
        df = f4f._name_fix(df)
        self.assertTrue('first_name' in df.columns)
        self.assertTrue('last_name' in df.columns)

    def test_f4f_to_dk_teams(self):
        df = self.df
        df['team'] = df['team'].apply(lambda x: f4f._f4f_to_dk_teams(x))
        self.assertTrue(len(df.query('team == "CHI"')) > 0)
        self.assertTrue(len(df.query('team == "XXX"')) == 0)

    def test_namestrip(self):
        nm = 'Odell Beckham Jr.'
        self.assertFalse(nm == f4f._namestrip(nm))
        self.assertFalse('Jr.' in f4f._namestrip(nm))

    def test_clean_df(self):
        df = pd.read_csv(self.projcsv)
        self.assertIsNotNone(df)
        df = f4f.clean_df(df)
        self.assertIsNotNone(df)
        self.assertTrue(len(df.query('team == "CHI"')) > 0)
        self.assertTrue('first_name' in df.columns)
        self.assertTrue('ffpts' in df.columns)

    def test_filter_players(self):
        df = pd.read_csv(self.projcsv)
        df = f4f.clean_df(df)
        df = f4f.filter_players(df)
        self.assertTrue(len(df.query('(pos == "QB") & (ffpts < 8)')) == 0)
        self.assertTrue(len(df.query('(pos == "QB") & (ffpts > 8)')) > 0)

    def test_add_salaries(self):
        df = pd.read_csv(self.projcsv)
        df = f4f.clean_df(df)
        df = f4f.filter_players(df)
        off_slate = ['CLE', 'NYJ', 'DET', 'NE', 'PIT', 'TB']
        df = df.query('team not in @off_slate').copy()
        df = f4f.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        self.assertTrue(len(df.query('salary > 5000')) > 0)

    def test_add_dst(self):
        df = pd.read_csv(self.projcsv)
        df = f4f.clean_df(df)
        df = f4f.filter_players(df)
        off_slate = ['CLE', 'NYJ', 'DET', 'NE', 'PIT', 'TB']
        df = df.query('team not in @off_slate').copy()
        df = f4f.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        df = f4f.add_dst(self.df)
        self.assertTrue(len(df.query('pos == "DST"')) > 0)

    def test_df_to_players(self):
        df = pd.read_csv(self.projcsv)
        df = f4f.clean_df(df)
        df = f4f.filter_players(df)
        off_slate = ['CLE', 'NYJ', 'DET', 'NE', 'PIT', 'TB']
        df = df.query('team not in @off_slate').copy()
        df = f4f.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        players = f4f.df_to_players(df)
        self.assertTrue(len(players) > 0)

    def test_optimizer_factory(self):
        df = pd.read_csv(self.projcsv)
        df = f4f.clean_df(df)
        df = f4f.filter_players(df)
        off_slate = ['CLE', 'NYJ', 'DET', 'NE', 'PIT', 'TB']
        df = df.query('team not in @off_slate').copy()
        df = f4f.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        players = f4f.df_to_players(df)
        o = f4f.optimizer_factory('dk', players)
        self.assertIsInstance(o, LineupOptimizer)
        self.assertIsNotNone(o.players)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()