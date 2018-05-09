# Drop report

from __future__ import absolute_import, print_function, division
 
import json
import os
import random

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

from nfl.scrapers.espn_fantasy import ESPNFantasyScraper
from nfl.parsers.espn_fantasy import ESPNFantasyParser

def run():
    profile = '/home/sansbacon/.mozilla/firefox/6h98gbaj.default'
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser('~'), '.fantasy'))
    scraper = ESPNFantasyScraper(config=config, profile=profile)
    parser = ESPNFantasyParser()

    with open('/home/sansbacon/.espnteams.json', 'r') as infile:
        for team in json.load(infile):
            league_id = team.get('leagueId')
            print('starting {}'.format(team.get('teamName')))
            content = scraper.drops(league_id)
            players = parser.drops(content)
            if players:
                for p in players:
                    print(p['transaction_date'])
                    print(p['transaction_description'])
            print('\n------------------\n')

if __name__ == '__main__':
    run()