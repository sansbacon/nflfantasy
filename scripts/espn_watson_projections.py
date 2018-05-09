import json
import logging
import time

from nfl.scrapers.espn import ESPNNFLScraper
from nfl.parsers.espn import ESPNNFLParser

def run(fn=None):
    scraper = ESPNNFLScraper(cache_name='Watson')
    players = scraper.watson_players()
    parser = ESPNNFLParser()

    projections = []
    for item in parser.watson_players(players):
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

    if fn:
        with open(fn, 'w') as outfile:
            json.dump(projections, outfile)
    return projections

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run('/home/sansbacon/watson/w17projections.json')