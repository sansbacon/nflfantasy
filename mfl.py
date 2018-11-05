import logging
import re

from bs4 import BeautifulSoup

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''
    def adp(self, season_year, franchises=12, ppr=1):
        '''
        Gets list of player ADP from myfantasyleague.com

        Args:
            season_year(int): 2018, etc.
            franchises(int): default 12 (number of teams)
            ppr(int): ppr leagues - 1, std 0, both -1

        Returns:
            dict: parsed json

        '''
        url = 'http://www03.myfantasyleague.com/{}/export?TYPE=adp&FRANCHISES={}&JSON=1&PPR={}'
        return self.get_json(url.format(season_year, franchises, ppr))

    def draft_results(self, season_year, league_id):
        '''

        Args:
            season_year(2018): calendar year of season start
            league_id(int): mfl-supplied numeric id of league

        Returns:
            dict

        '''
        url = 'http://www61.myfantasyleague.com/{}/export?TYPE=draftResults&L={}&JSON=1'
        return self.get_json(url.format(season_year, league_id))

    def league(self, season_year, league_id):
        '''

        Args:
            season_year(2018): calendar year of season start
            league_id(int): mfl-supplied numeric id of league

        Returns:
            dict

        '''
        url = 'http://www61.myfantasyleague.com/{}/export?TYPE=league&L={}&JSON=1'
        return self.get_json(url.format(season_year, league_id))

    def players(self, season_year):
        '''
        Gets list of players from myfantasyleague.com

        Args:
            season_year(int): 2018, etc.

        Returns:
            dict: parsed json

        '''
        url = 'http://www03.myfantasyleague.com/{}/export?TYPE=players&SINCE=&DETAILS=1&JSON=1'
        return self.get_json(url.format(season_year))


class Parser():
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def adp(self, content):
        '''
        Parses response and returns list of player dictionaries

        Args:
            content (dict): parsed json

        Returns:
            List of dictionaries if successful, empty list otherwise.

        '''
        return content['adp']['player']


    def players (self, content):
        '''
        Parses response and returns list of player dictionaries

        Args:
            content (dict): parsed json

        Returns:
            List of dictionaries if successful, empty list otherwise.

        '''
        return content['players']['player']


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()



if __name__ == '__main__':
    pass
