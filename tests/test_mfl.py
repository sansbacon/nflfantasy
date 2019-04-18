# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nflfantasy.mfl import Scraper


class MFL_test(unittest.TestCase):

    @property
    def season(self):
        return random.choice(range(2014, 2018))

    def setUp(self):
        self.s = Scraper()

    def test_players(self):
        content = self.s.players(self.season)
        self.assertIsNotNone(content)

    def test_adp(self):
        content = self.s.adp(season_year=2019, franchises=12, ppr=1)
        self.assertIsNotNone(content)

    def test_draft_results(self):
        content = self.s.draft_results(season_year=2019, league_id=49176)
        self.assertIsNotNone(content)

    def test_league(self):
        content = self.s.league(season_year=2019, league_id=49176)
        self.assertIsNotNone(content)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
