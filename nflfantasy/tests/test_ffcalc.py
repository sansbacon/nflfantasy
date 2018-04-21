# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.scrapers.ffcalc import FantasyFootballCalculatorScraper
from nfl.parsers.ffcalc import FantasyFootballCalculatorParser


class FFcalc_test(unittest.TestCase):

    @property
    def format(self):
        return random.choice(['ppr', 'standard'])

    @property
    def season(self):
        return random.choice(range(2013, 2017))

    @property
    def teams(self):
        return random.choice([8,10,12,14])

    def setUp(self):
        self.s = FantasyFootballCalculatorScraper(cache_name='ffc-test')
        self.p = FantasyFootballCalculatorParser()

    def test_adp(self):
        tm = self.teams
        content = self.s.adp()
        self.assertIsNotNone(content)
        content = self.s.adp(fmt=self.format)
        self.assertIsNotNone(content)
        players = self.p.adp(self.s.adp(teams=tm))
        self.assertIsNotNone(players)

    def test_adp_old(self):
        content = self.s.adp_old(season_year=self.season)
        self.assertIsNotNone(content)
        content = self.s.adp_old(season_year=self.season, fmt=self.format)
        self.assertIsNotNone(content)

    def test_projections(self):
        content = self.s.projections()
        self.assertIsNotNone(content)

if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()