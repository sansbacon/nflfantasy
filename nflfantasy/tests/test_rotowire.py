# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.scrapers.rotowire import RotowireNFLScraper


class RotowireNFL_test(unittest.TestCase):
    '''
    '''

    def setUp(self):
        self.s = RotowireNFLScraper()

    def test_dfs_week(self):
        content = self.s.dfs_week(2016, 22)
        self.assertIsNotNone(content)
        content = self.s.dfs_week(2016, 22, 'FanDuel')
        self.assertIsNotNone(content)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
