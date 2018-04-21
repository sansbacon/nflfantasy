# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import random
import sys
import unittest

from nfl.optimizers.preseasondfs import Lineup, PreseasonDfs
from nfl.utility import csv_to_dict

class preseasondfs_test(unittest.TestCase):

    def setUp(self):
        try:
            import os
            from pathlib import Path
            fn = os.path.join(str(Path.home()), 'w1.csv')
        except:
            import os
            from os.path import expanduser
            fn = os.path.join(expanduser('~'), 'w1.csv')
        self.ps = PreseasonDfs(list(csv_to_dict(fn)))

    def test_lineup(self):
        lu = Lineup()
        lu.add(self.ps.player('QB'))
        self.assertIsNotNone(lu.qb)
        lu.add(self.ps.player('RB'))
        self.assertIsNotNone(lu.rb)

    def test_random_stack(self):
        lu = self.ps.random_stack()
        self.assertIsNotNone(lu.qb)
        self.assertIsNotNone(lu.rb)
        self.assertIsNotNone(lu.wr)
        self.assertIsNotNone(lu.te)
        self.assertIsNotNone(lu.flex)
        self.assertIsNotNone(lu.dst)

if __name__=='__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    unittest.main()