# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.parsers.fftoday import FFTodayParser
from nfl.scrapers.fftoday import FFTodayScraper

class FFcalc_test(unittest.TestCase):

    @property
    def position(self):
        return random.choice(['qb', 'wr', 'te', 'rb'])

    @property
    def season(self):
        return random.choice(range(2013, 2017))

    @property
    def week(self):
        return random.choice(range(1,18))

    def setUp(self):
        self.s = FFTodayScraper(cache_name='fft-test')
        self.p = FFTodayParser()

    def test_position_id(self):
        content = self.s.position_id(self.position)
        self.assertIsNotNone(content)

    def test_weekly_results(self):
        # season, week, pos)
        content = self.s.weekly_results(self.season, self.week, self.position)
        self.assertIsNotNone(content)

    def test_weekly_rankings(self):
        # season, week, pos)
        content = self.s.weekly_rankings(self.season, self.week, self.position)
        self.assertIsNotNone(content)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()