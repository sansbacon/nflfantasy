# -*- coding: utf-8 -*-

import logging
import sys
import unittest

from nfl.scrapers.draft import DraftNFLScraper
from nfl.parsers.draft import DraftNFLParser
from nfl.agents.draft_headers import *


class DRAFT_test(unittest.TestCase):
    '''
    Tests DRAFT.com scraper, parser, agent

    '''
    def setUp(self):
        self.s = DraftNFLScraper(cache_name='test-draft-scraper')
        self.p = DraftNFLParser()

    def test_adp(self):
        content = self.s.adp(adp_headers)
        self.assertIsNotNone(content)
        players = self.p.players(content)
        self.assertIsNotNone(players)

    def test_complete_contests(self):
        content = self.s.complete_cases(cc_headers)
        self.assertIsNotNone(content)
        players = self.p.complete_contests(content)
        self.assertIsNotNone(players)

    def test_draft(self):
        content = self.s.draft(draft_headers)
        self.assertIsNotNone(content)
        players = self.p.draft(content)
        self.assertIsNotNone(players)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
