# scrapers/fantasymath.py

import logging

from nflmisc.scraper import FootballScraper


class FantasyMathScraper(FootballScraper):
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
