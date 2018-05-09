# Drop report

from __future__ import absolute_import, print_function, division
 
import json
import logging
import os
import pprint

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
    scraper = ESPNFantasyScraper(config = config, profile=profile)
    parser = ESPNFantasyParser()

    with open('/home/sansbacon/.espnteams.json', 'r') as infile:
        away_wanted = ['away_team', 'away_team_record', 'away_in_play', 'away_minutes_remaining', 'away_proj']
        home_wanted = ['home_team', 'home_team_record', 'home_in_play', 'home_minutes_remaining', 'home_proj']
        for team in json.load(infile)[0:2]:
            league_id = team.get('leagueId')
            print('starting {}'.format(team.get('teamName')))
            content = scraper.fantasy_league_scoreboard(league_id, 2017)
            for matchup in parser.fantasy_league_scoreboard(content):
                pprint.pprint(matchup)
                #print('\t'.join(['team', 'team_record', 'in_play', 'minutes_remaining', 'proj']))
                #print('\t'.join([matchup.get(k) for k in away_wanted]))
                #print('\t'.join([matchup.get(k) for k in home_wanted]))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()