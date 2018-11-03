# nflfantasy/tests/test_pipelines_ffa.py
# tests pipelines for ffa projections


import json
import logging
import os
from pathlib import Path
import random
import sys
import unittest

import pandas as pd
import feather
from pydfs_lineup_optimizer import LineupOptimizer, Player

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
        self._pff_mfl_dict = None

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
    def pos(self):
        return random.choice(['QB', 'WR', 'TE', 'RB'])

    @property
    def pff_position(self):
        return random.choice(self.pff_positions)

    @property
    def pff_positions(self):
        return ('qb', 'rb', 'wr', 'te', 'dst')


    @property
    def pff_projections(self):
        with open('data/pff/pff_projections.json', 'r') as f:
            return json.load(f)['player_projections']

    @property
    def pff_mfl_dict(self):
        if not self._pff_mfl_dict:
            q = """select pff_player_id as pid, mfl_player_id as mid
                   from dfs.pff_mfl_xref"""
            self._pff_mfl_dict = {p['pid']: p['mid'] for p in self.db.select_dict(q)}
        return self._pff_mfl_dict

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

    @unittest.skip
    def test_load(self):
        df = self.df
        col = self.col
        self.assertTrue(col in df.columns, 'Should have {} column'.format(col))

    @unittest.skip
    def test_keyd(self):
        keyd = ffa._keyd(self.db, self.season_year, self.week, self.source)
        self.assertIsInstance(keyd, dict)
        self.assertGreater(len(list(keyd.keys())), 0)

    @unittest.skip
    def test_mfld(self):
        keyd = ffa._mfld(self.db, self.season_year, self.week, self.source)
        self.assertIsInstance(keyd, dict)
        self.assertGreater(len(list(keyd.keys())), 0)
        self.assertIsInstance(list(keyd.keys())[0], int)

    @unittest.skip
    def test_name_fix(self):
        df = self.df
        df['full_name'] = df.apply(lambda x: ffa._name_fix(x), axis=1)
        self.assertTrue('full_name' in df.columns)

    @unittest.skip
    def test_fix_fdpos(self):
        self.assertEqual(ffa._fix_fdpos('DST'), 'D')
        pos = self.pos
        self.assertEqual(ffa._fix_fdpos(pos), pos)

    @unittest.skip
    def test_ffa_to_dk_teams(self):
        df = self.df
        df['team'] = df['team'].apply(lambda x: ffa._ffa_to_dk_teams(x))
        self.assertTrue(len(df.query('team == "CHI"')) > 0)
        self.assertTrue(len(df.query('team == "XXX"')) == 0)

    @unittest.skip
    def test_namestrip(self):
        nm = 'Odell Beckham Jr.'
        self.assertFalse(nm == ffa._namestrip(nm))
        self.assertFalse('Jr.' in ffa._namestrip(nm))

    @unittest.skip
    def test_clean_df(self):
        df = feather.read_dataframe(self.projfeather)
        self.assertIsNotNone(df)
        df = ffa.clean_df(df)
        self.assertIsNotNone(df)
        self.assertTrue(len(df.query('team == "CHI"')) > 0)
        self.assertTrue(self.col in df.columns)

    @unittest.skip
    def test_filter_players(self):
        df = feather.read_dataframe(self.projfeather)
        df = ffa.clean_df(df)
        df = ffa.filter_players(df)
        self.assertTrue(len(df.query('(position == "QB") & (points < 8)')) == 0)
        self.assertTrue(len(df.query('(position == "QB") & (points > 8)')) > 0)

    @unittest.skip
    def test_add_salaries(self):
        df = self.clean_df
        df = ffa.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        self.assertTrue(df['salary'].isna().sum() == 0)
        self.assertTrue(len(df.query('salary > 5000')) > 0)

    @unittest.skip
    def test_df_to_players(self):
        df = self.clean_df
        df = ffa.add_salaries(df=df, db=self.db, source=self.source,
                              season_year=self.season_year, week=self.week)
        players = ffa.df_to_players(df, self.source)
        self.assertTrue(len(players) > 0)

    @unittest.skip
    def test_optimizer_factory(self):
        df = self.clean_df
        df = ffa.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        self.assertTrue(df['salary'].isna().sum() == 0)
        self.assertTrue(len(df.query('salary > 5000')) > 0)
        players = ffa.df_to_players(df, self.source)
        self.assertTrue(len(players) > 0)
        o = ffa.optimizer_factory('dk', players)
        self.assertIsInstance(o, LineupOptimizer)
        self.assertIsNotNone(o.players)

    @unittest.skip
    def test_lineups_to_df(self):
        df = self.clean_df
        df = ffa.add_salaries(df, self.db, self.source,
                          self.season_year, self.week, False)
        players = ffa.df_to_players(df, self.source)
        o = ffa.optimizer_factory('dk', players)
        lineups = o.optimize(5)
        ldf = ffa.lineups_to_df(lineups)
        self.assertIsInstance(ldf, tuple)
        self.assertIsInstance(ldf[0], pd.DataFrame)

    def test_ffacols(self):
        pos = self.pff_position
        col = ffa.FFACOLS.get(pos)
        self.assertIsInstance(col, list)
        self.assertGreater(len(col), 10)

    def test_ffakeys(self):
        pos = self.pff_position
        keys = ffa.PFFKEY_TO_FFAKEY.get(pos)
        self.assertIsInstance(keys, dict)
        self.assertGreater(len(keys), 5)

    def test_pff_to_ffa(self):
        players = self.pff_projections
        ffa_players = ffa.pff_to_ffa(players, self.pff_mfl_dict)
        self.assertIsInstance(ffa_players, list)
        self.assertGreater(len(ffa_players), 0)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
