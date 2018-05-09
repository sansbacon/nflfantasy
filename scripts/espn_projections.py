import json
import random

from nfl.names import first_last
from nfl.scrapers.espn import ESPNNFLScraper
from nfl.parsers.espn import ESPNNFLParser

scraper = ESPNNFLScraper()
parser = ESPNNFLParser()
fantasy_players = []

offsets = {
  'qb': [0, 40, 80, 120],
  'rb': [0, 40, 80, 120, 160, 200, 240],
  'wr': [0, 40, 80, 120, 160, 200, 240, 280, 320, 360],
  'te': [0, 40, 80, 120, 160],
  'k': [0, 40]
}

for pos in ['qb', 'rb', 'wr', 'te', 'k']:
    for offset in offsets.get(pos):
        content = scraper.projections(pos, offset)
        fantasy_players += parser.projections(content, pos)
        print('finished {} {}'.format(pos, offset))

#with open('/home/sansbacon/espn-fantasy-players.json', 'w') as outfile:
#    json.dump(fantasy_players, outfile)
