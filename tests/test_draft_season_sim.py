# -*- coding: utf-8 -*-

import logging
import random
import sys
import unittest

from nflfantasy.simulators.playdraft_sim import *


class DRAFT_season_sim_test(unittest.TestCase):
    '''
    Tests DRAFT.com scraper, parser, agent

    '''

    @property
    def pos(self):
        return random.choice(('rb'))

    @property
    def n(self):
        return random.randint(1, 7)

    def setUp(self):
        self.df = get_data()

    def test_get_data(self):
        df = get_data()
        self.assertIsNotNone(df)

    def test_n_players(self):
        rndp = n_players(self.df, self.pos, self.n, 'tiered')
        self.assertIsNotNone(rndp)

if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
