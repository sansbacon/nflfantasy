# -*- coding: utf-8 -*-
# nflfantasy/fantasymath.py
# scraper/parser for fantasymath.com fantasy resources

import logging
import re

from bs4 import BeautifulSoup

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''

    def __init__(self, headers=None, cookies=None, cache_name=None,
                 delay=1, expire_hours=168, as_string=False):
        '''
        Scrape fantasymath API

        Args:
            headers: dict of headers
            cookies: cookiejar object
            cache_name: should be full path
            delay: int (be polite!!!)
            expire_hours: int - default 168
            as_string: get string rather than parsed json
        '''
        FootballScraper.__init__(self, headers, cookies, cache_name, delay, expire_hours, as_string)
        self.headers.update({'origin': 'https://fantasymath.com',
                             'authority': 'api.fantasymath.com',
                             'referer': 'https://fantasymath.com/'})

    def distribution(self, player_codes):
        '''
        Gets projection distribution for specified players

        Args:
            player_codes(list): of str

        Returns:
            dict

        '''
        if isinstance(player_codes, str):
            player_codes = [player_codes]

        url = 'https://api.fantasymath.com/v2/players-wdis/'
        params = {'wdis': player_codes,
                  'dst': 'mfl',
                  'qb': 'pass4',
                  'scoring': 'ppr'}

        return self.get_json(url, params)

    def players(self):
        '''
        Gets projection distribution for specified players

        Args:
            player_codes(list): of str

        Returns:
            dict

        '''
        url = 'https://api.fantasymath.com/players'
        return self.get_json(url)


class Parser():
    '''
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _fix_val(self, v):
        '''
        Fixes various values

        Args:
            v:

        Returns:

        '''
        if isinstance(v, float):
            return round(v, 2)
        else:
            return v


    def distributions(self, content):
        '''
        Parses player distribution JSON

        Args:
            content (dict): parsed JSON

        Returns:
            list: of player dict

        '''
        wanted = ['fp_id', 'name', 'p25', 'p5', 'p50', 'p75', 'p95', 'pos', 'prob',
                  'proj', 'scoring', 'std']
        return [{k: self._fix_val(v) for k,v in p.items() if k in wanted} for
                p in content['players']]


    def players(self, content):
        '''
        Parses players JSON

        Args:
            content (dict): parsed JSON

        Returns:
            dict

        '''
        fm_players = {}
        for p in content:
            vals = p['label'].split()
            d = {'id': p['value'], 'pos': vals[0], 'name': ' '.join(vals[1:])}
            fm_players[d['id']] = d
        return fm_players


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()

    def weekly_projections(self):
        '''
        Gets weekly projections

        Args:
            week(int):

        Returns:
            list: of dict

        '''
        pass
        #content = self._s.weekly_projections()
        #return self._p.weekly_projections(content)


if __name__ == '__main__':
    pass
