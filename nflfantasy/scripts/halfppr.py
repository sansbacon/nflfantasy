# half-ppr projections

from pprint import pprint
import random

from nfl.scrapers.ffnerd import FFNerdNFLScraper
from nfl.parsers.ffnerd import FFNerdNFLParser

scraper = FFNerdNFLScraper(api_key='8x3g9y245w6a')
parser = FFNerdNFLParser()

players = []
for pos in ['QB', 'RB', 'WR', 'TE']:
    players += parser.weekly_rankings(scraper.weekly_rankings(14, pos))

for idx, p in enumerate(players):
    try:
        players[idx]['ppr'] = float(p['ppr'])
        players[idx]['standard'] = float(p['standard'])
        p['hppr'] = round((players[idx]['standard'] + players[idx]['ppr']) / 2, 2)
    except:
        pass

pprint(random.sample(players, 5))