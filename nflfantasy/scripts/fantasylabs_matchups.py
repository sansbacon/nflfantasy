import json         
import os
import time                                                     

from nfl.scrapers.fantasylabs import FantasyLabsNFLScraper
from nfl.seasons import fantasylabs_week

scraper = FantasyLabsNFLScraper() 
gd = fantasylabs_week(2017, 2)

games = scraper.games(2017, 2)
teams = [g['Properties']['Team'] for g in games['TeamMatchups']]                 
                             
for t in teams:                  
    logging.info('starting {}'.format(t))
    matchup = scraper.matchups(t, gd)
    try:
        from pathlib import Path
        dirn = os.path.join(str(Path.home()), 'matchups-2017-w2')
    except:
        from os.path import expanduser
        dirn = os.path.join(expanduser('~'), 'matchups-2017-w2')
    
    fn = '{}_{}_matchup.json'.format(t, gd)
    with open(os.path.join(dirn, fn), 'w') as outfile:
        json.dump(matchup, outfile)         
    logging.info('finished {}'.format(t))               
    time.sleep(1) 
