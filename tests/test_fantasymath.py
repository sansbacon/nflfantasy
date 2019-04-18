'''

# tests/test_fantasymath.py

'''

import logging
import random
import sys
import unittest

from nflfantasy.fantasymath import Scraper, Parser


class fantasymath_test(unittest.TestCase):
    '''
    Tests DRAFT.com scraper, parser, agent

    '''
    def setUp(self):
        self.s = Scraper()
        self.p = Parser()

    @property
    def player_codes(self):
        pc = ['jalen-richard', 'royce-freeman',
         'matt-ryan', 'rashaad-penny',
         'travis-kelce', 'andy-dalton', 'austin-hooper']
        return random.sample(pc, random.randint(2,3))

    def test_players(self):
        content = self.s.players()
        self.assertIsNotNone(content)
        players = self.p.players(content)
        self.assertIsNotNone(players)
        self.assertIsInstance(players, dict)

    def test_distribution(self):
        content = self.s.distribution(self.player_codes)
        self.assertIsNotNone(content)
        dist = self.p.distribution(content)
        self.assertIsNotNone(dist)
        self.assertIsInstance(dist, list)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
