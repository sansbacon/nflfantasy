'''

# nflfantasy/mfl.py

'''

import logging

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):
    '''
    Scrapes mfl API

    '''

    def __init__(self, cache_name='mfl-scraper', **kwargs):
        '''

        Args:
            cache_name:
            **kwargs:

        Returns:
            Scraper

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        super().__init__(cache_name=cache_name, **kwargs)

    @property
    def base_url(self):
        return 'http://www03.myfantasyleague.com/{}/export?'


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
        url = self.base_url.format(season_year)
        params = {
            'TYPE': 'adp',
            'FRANCHISES': franchises,
            'PPR': ppr,
            'JSON': 1
        }
        return self.get_json(url, params=params)

    def draft_results(self, season_year, league_id):
        '''

        Args:
            season_year(2018): calendar year of season start
            league_id(int): mfl-supplied numeric id of league

        Returns:
            dict

        '''
        url = self.base_url.format(season_year)
        params = {
            'TYPE': 'draftResults',
            'L': league_id,
            'JSON': 1
        }
        return self.get_json(url, params=params)

    def league(self, season_year, league_id):
        '''

        Args:
            season_year(2018): calendar year of season start
            league_id(int): mfl-supplied numeric id of league

        Returns:
            dict

        '''
        url = self.base_url.format(season_year)
        params = {
            'TYPE': 'league',
            'L': league_id,
            'JSON': 1
        }
        return self.get_json(url, params=params)

    def players(self, season_year, since=None, details=1):
        '''
        Gets list of players from myfantasyleague.com

        Args:
            season_year(int): 2018, etc.
            since(int): unix timestamp
            details(int): 1 for details, 0 if not

        Returns:
            dict: parsed json

        '''
        url = self.base_url.format(season_year)
        params = {
            'TYPE': 'players',
            'SINCE': since,
            'DETAILS': details,
            'JSON': 1
        }
        return self.get_json(url, params=params)


class Parser():
    '''
    Parses mfl API

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

    def draft_results(self, content):
        '''
        Parses response and returns list of draft picks

        Args:
            content (dict): parsed json

        Returns:
            List of dictionaries if successful, empty list otherwise.

        '''
        return content['draftResults']

    def league(self, content):
        '''
        Parses response and returns list of teams in league

        Args:
            content (dict): parsed json

        Returns:
            List of dictionaries if successful, empty list otherwise.

        '''
        return content['league']

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

    def __init__(self, season_year, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.season_year = season_year
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()

    def adp(self, franchises=12, ppr=1):
        '''

        Returns:

        '''
        content = self._s.adp(self.season_year, franchises, ppr)
        return self._p.adp(content)

    def players(self, since=None, details=1):
        '''

        Returns:

        '''
        content = self._s.players(self.season_year, since, details)
        return self._p.players(content)


if __name__ == '__main__':
    pass
