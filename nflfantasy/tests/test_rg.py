# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.scrapers.rotoguru import RotoguruNFLScraper
from nfl.parsers.rotoguru import RotoguruNFLParser


class RotoguruNFL_test(unittest.TestCase):
    '''
    '''

    @property
    def game(self):
        return random.choice(['dk', 'fd'])

    @property
    def season(self):
        return random.choice(range(2014, 2017))

    @property
    def week(self):
        return random.choice(range(1, 18))

    def setUp(self):
        self.s = RotoguruNFLScraper(cache_name='test-rg-scraper')
        self.p = RotoguruNFLParser()

    def test_dfs_week(self):
        content = self.s.dfs_week(self.season, self.week, self.game)
        self.assertIsNotNone(content)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
