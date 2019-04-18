# tests/test_fantasypros.py

import logging
import random
import sys
import unittest

from nflfantasy.fantasypros import Parser, Scraper
from nfl.seasons import current_season_year


class TestFantasyProsScraper(unittest.TestCase):

    @property
    def std_positions(self):
        return random.choice(['qb', 'k', 'dst'])

    @property
    def ppr_positions(self):
        return random.choice(['rb', 'wr', 'te', 'flex', 'qb-flex'])

    def setUp(self):
        self.s = Scraper(cache_name='fpros-test')
        self.p = Parser()
        self.season_year = current_season_year()

    def test_adp(self):
        fmt = 'std'
        content = self.s.adp(fmt=fmt)
        players = self.p.adp(content, self.season_year, fmt)
        self.assertIsNotNone(players)
        fmt = 'ppr'
        content = self.s.adp(fmt=fmt)
        players = self.p.adp(content, self.season_year, fmt)
        self.assertIsNotNone(players)

    def test_draft_rankings(self):
        content = self.s.draft_rankings(pos=self.std_positions, fmt='std')
        ranks = self.p.draft_rankings_overall(content)
        self.assertIsNotNone(ranks)

    def test_projections(self):
        pos = self.std_positions
        content = self.s.projections(pos, fmt='std', week='draft')
        proj = self.p.projections(content, pos)
        self.assertIsNotNone(proj)
        pos = self.ppr_positions
        content = self.s.projections(pos, fmt='ppr', week='draft')
        proj = self.p.projections(content, pos)
        self.assertIsNotNone(proj)

    @unittest.skip
    def test_ros_rankings(self):
        pass

        '''
        pos = self.std_positions
        self.assertIsNotNone(self.p.ros_rankings(self.s.ros_rankings(pos, fmt='std', week='draft'), pos))
        pos = self.ppr_positions
        self.assertIsNotNone(self.p.ros_rankings(self.s.ros_rankings(pos, fmt='ppr', week='draft'), pos))
        self.assertIsNotNone(self.p.ros_rankings(self.s.ros_rankings(pos, fmt='hppr', week='draft'), pos))
        '''

    def test_weekly_rankings(self):
        pos = self.std_positions
        season_year = 2018
        week = 1
        fmt = 'std'
        content = self.s.weekly_rankings(pos, fmt, week)
        ranks = self.p.weekly_rankings(content, fmt, pos, season_year, week)
        self.assertIsNotNone(ranks)

    def test_player_weekly_rankings(self):
        content = self.s.player_weekly_rankings(pid='tom-brady', week=2, fmt='STD')
        self.assertIn('Koerner', content, 'content should have Sean Koerners rankings')
        ranks = self.p.player_weekly_rankings(content)
        self.assertGreaterEqual(len(ranks), 1)


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
