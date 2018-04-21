# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging, os, sys, unittest

from nfl.scrapers.intertops import IntertopsNFLScraper


class TestIntertops(unittest.TestCase):


    def setUp(self):
        self.s = IntertopsNFLScraper(api_key=os.environ['INTERTOPS_API_KEY'])

    def test_categories(self):
        #content = self.s.categories()
        #self.assertIsNotNone(content)
        pass

    def test_odds(self):
        #content = self.s.odds(delta=60)
        #self.assertIsNotNone(content)
        pass


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()