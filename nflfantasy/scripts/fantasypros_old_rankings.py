import logging, os

from nfl.dates import *
from nfl.db.nflpg import NFLPostgres
from nfl.parsers.fantasypros import FantasyProsNFLParser
from nfl.pipelines.fantasypros import *
from nfl.scrapers.fantasypros import FantasyProsWaybackNFLScraper
from nfl.seasons import *


logging.basicConfig(level=logging.INFO)
s = FantasyProsWaybackNFLScraper(cache_name='fpros-wb')
p = FantasyProsNFLParser()
db = NFLPostgres(user=os.environ['PG_NFLDB_USER'], password=os.environ['PG_NFLDB_PASSWORD'], database='nfldb')

for seas in [2015]:
    for week in range(1, 18):
        for pos in ['qb', 'wr', 'te', 'rb', 'dst']:
            start = week_start(seas, week)
            try:
                content, ts = s.weekly_rankings(pos, 'std', datetostr(start, 'db'))
                if content:
                    rankings = p.weekly_rankings(content)
                    for ranking in weekly_rankings_table(rankings, seas):
                        db._insert_dict(ranking, 'weekly_rankings')
                    logging.info('finished {} week {} pos {}'.format(seas, week, pos))
                else:
                    logging.info('no content for {} week {} pos {}'.format(seas, week, pos))
            except Exception as e:
                logging.exception('could not get week {} pos {}: {}'.format(week, pos, e))