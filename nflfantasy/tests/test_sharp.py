# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.scrapers.sharp import SharpScraper


class RotoguruNFL_test(unittest.TestCase):
    '''
    '''
    def setUp(self):
        self.s = SharpScraper()

    def test_odds(self):
        content = self.s.odds()
        self.assertIsNotNone(content)
        self.assertIn('SCHEDULE', content)

if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
