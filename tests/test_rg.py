# tests/test_rg.py

import logging
import random
import sys
import unittest

from nflfantasy.rotoguru import Scraper, Parser


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
        self.s = Scraper(cache_name='test-rg-scraper')
        self.p = Parser()

    def test_dfs_week(self):
        content = self.s.dfs_week(self.season, self.week, self.game)
        results = self.p.dfs_week(content)
        self.assertIsNotNone(results)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
