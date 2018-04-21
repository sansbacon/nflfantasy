# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import sys
import unittest

from nfl.parsers.fantasydata import FantasyDataNFLParser


class Fantasydata_test(unittest.TestCase):
    '''
    Tests nfldotcom scraper and parser
    '''

    def setUp(self):
        self.p = FantasyDataNFLParser()
        self.stream_handler = logging.StreamHandler(sys.stdout)

    def test_dst(self):
        with open('data/DST.html', 'r') as infile:
            content = infile.read()
        results = self.p.dst(content, season=2002, week=1)
        logging.info(results)
        self.assertIsNotNone(results)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
