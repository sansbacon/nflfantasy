# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.scrapers.fantasylabs import FantasyLabsNFLScraper
from nfl.parsers.fantasylabs import FantasyLabsNFLParser


class FantasyLabs_test(unittest.TestCase):

    @property
    def gamedate(self):
        return random.choice(['09_07_2016', '09_21_2016', '09_28_2016'])

    def setUp(self):
        self.s = FantasyLabsNFLScraper(cache_name='fl-test')
        self.p = FantasyLabsNFLParser()

    def test_games_day(self):
        content = self.s.games_day(self.gamedate)
        self.assertIsNotNone(content)
        self.assertIsInstance(content, list)

    def test_model(self):
        content = self.s.model(self.gamedate)
        self.assertIsNotNone(content)
        self.assertIsInstance(content, dict)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()