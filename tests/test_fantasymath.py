# -*- coding: utf-8 -*-

import logging
import random
import sys
import unittest

from nflfantasy.scrapers.fantasymath import FantasyMathScraper
from nflfantasy.parsers.fantasymath import FantasyMathParser


class fantasymath_test(unittest.TestCase):
    '''
    Tests DRAFT.com scraper, parser, agent

    '''
    def setUp(self):
        self.s = FantasyMathScraper()
        self.p = FantasyMathParser()

    @property
    def player_codes(self):
        pc = ['justin-tucker', 'marshawn-lynch',
         'jalen-richard', 'jacksonville-defense', 'royce-freeman',
         'matt-ryan', 'rashaad-penny',
         'travis-kelce', 'andy-dalton', 'austin-hooper']
        return random.sample(pc, random.randint(1,3))

    def test_players(self):
        content = self.s.players()
        self.assertIsNotNone(content)
        players = self.p.players(content)
        self.assertIsNotNone(players)
        self.assertIsInstance(players, dict)

    def test_distribution(self):
        content = self.s.distribution(self.player_codes)
        self.assertIsNotNone(content)
        dist = self.p.distributions(content)
        self.assertIsNotNone(dist)
        self.assertIsInstance(dist, list)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
