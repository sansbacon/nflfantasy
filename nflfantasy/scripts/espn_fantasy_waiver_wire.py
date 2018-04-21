# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import json
import logging
import os

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from nfl.scrapers.espn_fantasy import ESPNFantasyScraper
from nfl.parsers.espn_fantasy import ESPNFantasyParser
from nfl.utility import getdb


def run():
    db = getdb()
    profile = '/home/sansbacon/.mozilla/firefox/6h98gbaj.default'
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.fantasy'))
    s = ESPNFantasyScraper(config=config, profile=profile)
    parser = ESPNFantasyParser()

    with open('/home/sansbacon/.espnteams.json', 'r') as infile:
        teams = json.load(infile)

    for team in teams:
        positions = ['qb', 'rb', 'wr', 'te', 'dst']
        if team.get('k') == 1:
            positions.append('k')
        logging.info('starting {}'.format(team['leagueName']))
        for pos in positions:
            logging.info('starting {} {}'.format(team['leagueName'], pos))
            content = s.fantasy_waiver_wire(team_id=team.get('teamId'), league_id=team.get('leagueId'),
                                            season=team.get('seasonId'), position=pos)
            if content:
                players = parser.fantasy_waiver_wire(content)
                if players:
                    for idx, pl in enumerate(players):
                        players[idx]['source_league_id'] = team.get('leagueId')
                        players[idx]['season_year'] = team.get('seasonId')
                        players[idx]['source_league_size'] = team.get('leagueSize')
                    db.insert_dicts(players, 'extra_fantasy.espn_waiver_wire')
                    logging.info('finished {} {}'.format(team['leagueName'], pos))
                else:
                    logging.error('could not get players for {}'.format(pos))
            else:
                logging.error('could not get {}'.format(pos))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()