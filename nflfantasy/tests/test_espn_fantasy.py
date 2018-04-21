# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import os
import random
import sys
import unittest

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from nfl.scrapers.espn_fantasy import ESPNFantasyScraper
from nfl.parsers.espn_fantasy import ESPNFantasyParser


class ESPN_fantasy_test(unittest.TestCase):
    '''
    Tests espn_fantasy scraper and parser
    '''

    @property
    def pos(self):
        return random.choice(['qb', 'rb', 'wr', 'k', 'te'])

    def offset(self, pos=None):
        if not pos:
            pos = self.pos
        if pos == 'k':
            return 0
        elif pos in ['qb', 'te']:
            return random.choice([0, 50])
        else:
            return random.choice([0, 50, 100])

    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(os.path.expanduser('~'), '.fantasy'))
        self.s = ESPNFantasyScraper(config=self.config)
        self.p = ESPNFantasyParser()
        self.leagueId = 483232
        self.teamId = 7
        self.seasonId = 2017

    def test_fantasy_league_rosters(self):
        content = self.s.fantasy_league_rosters(self.leagueId)
        self.assertIsNotNone(content)
        self.assertIn('QB', content)
        players = self.p.fantasy_league_rosters(content)
        self.assertIsNotNone(players)

    def test_fantasy_team_roster(self):
        content = self.s.fantasy_team_roster(league_id=self.leagueId,team_id=self.teamId, season=self.seasonId)
        self.assertIn('Acquisitions', content)
        players = self.p.fantasy_team_roster(content)
        self.assertIsNotNone(players)

    def test_waiver_wire(self):
        # league_id, team_id, season
        content = self.s.fantasy_waiver_wire(self.leagueId, self.teamId, self.seasonId)
        self.assertIn('/ffl/freeagency?', content)

        # league_id, team_id, season, start_index=None
        pos = self.pos
        content = self.s.fantasy_waiver_wire(self.leagueId, self.teamId, self.seasonId, self.offset())
        self.assertIn('/ffl/freeagency?', content)

        # league_id, team_id, season, start_index=None, position=None
        pos = self.pos
        content = self.s.fantasy_waiver_wire(self.leagueId, self.teamId, self.seasonId, self.offset(pos), pos)
        self.assertIn('/ffl/freeagency?', content)

        players = self.p.fantasy_waiver_wire(content)
        self.assertIsNotNone(players)


if __name__=='__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    unittest.main()
