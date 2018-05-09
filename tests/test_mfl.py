# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.scrapers.mfl import MFLScraper


class MFL_test(unittest.TestCase):

    @property
    def season(self):
        return random.choice(range(2014, 2018))

    def setUp(self):
        self.s = MFLScraper()

    def test_players(self):
        content = self.s.players(self.season)
        self.assertIsNotNone(content)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
