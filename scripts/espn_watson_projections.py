import json
import logging
import time

import click

from nfl.scrapers.espn import ESPNNFLScraper
from nfl.parsers.espn import ESPNNFLParser

@click.command()
@click.option('--filename', default=None, help='file to save')
def run(filename):
    scraper = ESPNNFLScraper(cache_name='Watson')
    players = scraper.watson_players()
    parser = ESPNNFLParser()

    projections = []
    for item in parser.watson_players(players)[0:2]:
        try:
            pid = item.get('playerid')
            content = scraper.watson(pid)
            player = parser.watson(content)
            player['full_name'] = item.get('full_name')
            player['position'] = item.get('position')
            projections.append(player)
            logging.info('finished {}'.format(player['full_name']))
            time.sleep(.5)

        except:
            logging.exception('no pid: {}'.format(item))

    if filename:
        with open(filename, 'w') as outfile:
            json.dump(projections, outfile)
    return projections


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()