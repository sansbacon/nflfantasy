# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import os
import random
import sys
import unittest

from nfl.parsers.ffnerd import FFNerdNFLParser
from nfl.scrapers.ffnerd import FFNerdNFLScraper


class TestFFNerdScraper(unittest.TestCase):

    @property
    def position(self):
        return random.choice(['QB', 'RB', 'WR', 'TE'])

    @property
    def season(self):
        return random.choice(range(2010, 2017))

    @property
    def team(self):
        return random.choice(['WAS', 'ARI', 'CHI', 'DET'])

    @property
    def week(self):
        return random.choice(range(1, 18))

    def setUp(self):
        self.s = FFNerdNFLScraper(api_key=os.getenv('FFNERD_API_KEY'),
                                  cache_name='test-ffnerd-scraper')
        self.p = FFNerdNFLParser()

    '''
    def test_depth_charts(self):
        content = self.s.depth_charts()
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.depth_charts(content))

    def test_draft_projections(self):
        content = self.s.draft_projections(self.position)
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.draft_projections(content))

    def test_draft_rankings(self):
        content = self.s.draft_rankings()
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.draft_rankings(content))

    def test_draft_tiers(self):
        content = self.s.draft_tiers()
        self.assertIsInstance(content, list)
        self.assertIsNotNone(self.p.draft_tiers(content))

    def test_injuries(self):
        content = self.s.injuries(self.week)
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.injuries(content))

    '''
    def test_players(self):
        content = self.s.players()
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.players(content))
        content = self.s.players(self.position)
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.players(content))

    '''
    def test_schedule(self):
        content = self.s.schedule()
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.schedule(content))

    def test_weekly_projections(self):
        content = self.s.weekly_projections(self.week, self.position)
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.weekly_projections(content))

    def test_weekly_rankings(self):
        content = self.s.weekly_rankings(self.week, self.position)
        self.assertIsInstance(content, dict)
        self.assertIsNotNone(self.p.weekly_rankings(content))
    '''

if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()