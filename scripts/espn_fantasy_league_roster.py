# -*- coding: utf-8 -*-
# espn_fantasy_league_roster.py

from __future__ import absolute_import, print_function, division

import json
import logging
import os
import random

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from nfl.scrapers.espn_fantasy import ESPNFantasyScraper
from nfl.parsers.espn_fantasy import ESPNFantasyParser
from nfl.utility import getdb


def run():
    profile = '/home/sansbacon/.mozilla/firefox/6h98gbaj.default'
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.fantasy'))
    s = ESPNFantasyScraper(config=config, profile=profile)
    parser = ESPNFantasyParser()
    db = getdb()

    with open('/home/sansbacon/.espnteams.json', 'r') as infile:
        teams = json.load(infile)

    all_players = []

    for team in teams:
        content = s.fantasy_league_rosters(team['leagueId'])
        players = parser.fantasy_league_rosters(content)

        if players:
            for idx, pl in enumerate(players):
                players[idx]['source_league_size'] = team.get('leagueSize')
            print(random.choice(players))
            db.insert_dicts(players, 'extra_fantasy.espn_league_roster')
            all_players += players
            print('finished {}'.format(team['leagueName']))
        else:
            print('could not get players for {}'.format(team['leagueName']))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()