'''
PinnacleNFLParser
http://xml.pinnaclesports.com/pinnaclefeed.aspx?sporttype=Football&sportsubtype=nfl
<event> contains game date, team names, o/u, point spread, can calculate implied totals
'''

import datetime
import logging

from bs4 import BeautifulSoup
import dateparser

from nfl import nflseasons
from nfl import teams

class PinnacleNFLParser:
    '''
    Takes xml from scraper, returns list of game dictionaries
    '''

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _implied_total(self, game_total, spread):
        '''
        Takes game total and spread and returns implied total based on those values
        '''
    
        return (float(game_total)/float(2)) - (float(spread)/float(2))

    def odds(self, xml):
        '''
        Takes xml in, returns list of game dictionaries:
        
        '''
        games = []

        # get the list of events
        soup = BeautifulSoup(xml, 'lxml')
        events = soup.findAll('event')
        logging.debug('there are {0} events'.format(len(events)))

        # last item is unwanted - All NFL Games Will Have Second Half Wagering
        # revisit this once season starts - exclude last event?
        for event in events:
            game = {}

            # game information
            gd = event.find('event_datetimegmt').string
            d = dateparser.parse(gd, settings={'TIMEZONE': 'US/Eastern'})
            game['game_date'] = datetime.datetime.strftime(d, '%m-%d-%Y')
            sy = nflseasons.season_week(d.date())
            if sy:
                game['season'] = sy['season']
                game['week'] = sy['week']

            # teams
            away, home = event.findAll('participant')
            game['away_team'] = teams.long_to_code(away.find('participant_name').string)
            game['home_team'] = teams.long_to_code(home.find('participant_name').string)

            # lines
            period = event.find('period')
            spread = period.find('spread')
            svis = float(spread.find('spread_visiting').string)
            shome = float(spread.find('spread_home').string)
            mlaway = period.find('moneyline_visiting')
            if mlaway: game['away_ml'] = mlaway.string
            mlhome = period.find('moneyline_home')
            if mlhome: game['home_ml'] = mlhome.string

            if svis > shome:
                game['spread'] = shome
                game['favorite'] = game['home_team']
                game['underdog'] = game['away_team']

            elif svis < shome:
                game['spread'] = svis
                game['favorite'] = game['away_team']
                game['underdog'] = game['home_team']

            else:
                # spreads equal
                game['spread'] = 0
                game['favorite'] = None
                game['underdog'] = None

            # totals, including calculated implied totals
            game['total'] = float(period.find('total_points').string)
            game['home_total'] = self._implied_total(game_total=game['total'], spread=shome)
            game['away_total'] = self._implied_total(game_total=game['total'], spread=svis)

            # add to list
            games.append(game)

        return games

if __name__ == '__main__':
    pass
