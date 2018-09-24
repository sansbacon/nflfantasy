import logging
import os
from pathlib import Path
import random
import sys
import unittest

import feather
from pydfs_lineup_optimizer import LineupOptimizer

from nfl.utility import getdb
from nflfantasy.pipelines import ffa


class Ffa_pipeline_test(unittest.TestCase):
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
    def clean_df(self):
        df = feather.read_dataframe(self.projfeather)
        df = ffa.clean_df(df)
        df = ffa.filter_players(df)
        off_slate = ['CLE', 'NYJ', 'DET', 'NE', 'PIT', 'TB']
        return df.query('team not in @off_slate').copy()

    @property
    def col(self):
        return random.choice(['points', 'first_name', 'position'])

    @property
    def df(self):
        if not self._df:
            self._df = feather.read_dataframe(self.projfeather)
            self._df.columns = self._df.columns.str.lower()
        return self._df

    @property
    def fn(self):
        return '{}_w{}_ffa-{}proj.feather'.format(self.season_year,
                                              self.week, self.source)
    @property
    def projfeather(self):
        return self.projdir / 'ffa' / self.fn

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

    def test_name_fix(self):
        df = self.df
        df['full_name'] = df.apply(lambda x: ffa._name_fix(x), axis=1)
        self.assertTrue('full_name' in df.columns)

    def test_ffa_to_dk_teams(self):
        df = self.df
        df['team'] = df['team'].apply(lambda x: ffa._ffa_to_dk_teams(x))
        self.assertTrue(len(df.query('team == "CHI"')) > 0)
        self.assertTrue(len(df.query('team == "XXX"')) == 0)

    def test_namestrip(self):
        nm = 'Odell Beckham Jr.'
        self.assertFalse(nm == ffa._namestrip(nm))
        self.assertFalse('Jr.' in ffa._namestrip(nm))

    def test_clean_df(self):
        df = feather.read_dataframe(self.projfeather)
        self.assertIsNotNone(df)
        df = ffa.clean_df(df)
        self.assertIsNotNone(df)
        self.assertTrue(len(df.query('team == "CHI"')) > 0)
        self.assertTrue(self.col in df.columns)

    def test_filter_players(self):
        df = feather.read_dataframe(self.projfeather)
        df = ffa.clean_df(df)
        df = ffa.filter_players(df)
        self.assertTrue(len(df.query('(position == "QB") & (points < 8)')) == 0)
        self.assertTrue(len(df.query('(position == "QB") & (points > 8)')) > 0)

    def test_add_salaries(self):
        df = self.clean_df
        df = ffa.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        self.assertTrue(df['salary'].isna().sum() == 0)
        self.assertTrue(len(df.query('salary > 5000')) > 0)

    def test_df_to_players(self):
        df = self.clean_df
        df = ffa.add_salaries(df=df, db=self.db, source=self.source,
                              season_year=self.season_year, week=self.week)
        players = ffa.df_to_players(df)
        self.assertTrue(len(players) > 0)

    def test_optimizer_factory(self):
        df = self.clean_df
        df = ffa.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        self.assertTrue(df['salary'].isna().sum() == 0)
        self.assertTrue(len(df.query('salary > 5000')) > 0)
        players = ffa.df_to_players(df)
        self.assertTrue(len(players) > 0)
        o = ffa.optimizer_factory('dk', players)
        self.assertIsInstance(o, LineupOptimizer)
        self.assertIsNotNone(o.players)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()