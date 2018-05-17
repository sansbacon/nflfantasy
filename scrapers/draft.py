# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import json

from nflmisc.scraper import FootballScraper


class DraftNFLScraper(FootballScraper):
    '''
    '''

    def _json_file(self, fn):
        '''
        Opens JSON file from disk

        Args:
            fn: 

        Returns:
            dict: JSON parsed into dict
            
        '''
        with open(fn, 'r') as infile:
            return json.load(infile)

    def adp(self, headers=None, fn=None):
        '''

        Args:
            headers (dict): 

        Returns:
            dict

        '''
        if headers and not fn:
            url = 'https://api.playdraft.com/v4/player_pool/11416'
            self.headers = headers
            return self.get_json(url=url)
        elif fn and not headers:
            return self._json_file(fn)
        else:
            raise ValueError('Must pass headers or fn')

    def complete_cases(self, headers, fn):
        '''
    
        Args:
            headers (dict): 
    
        Returns:
            dict
    
        '''
        if headers and not fn:
            url = 'https://api.playdraft.com/v1/window_clusters/2015/complete_contests'
            self.headers = headers
            return self.get_json(url=url)
        elif fn and not headers:
            return self._json_file(fn)
        else:
            raise ValueError('Must pass headers or fn')

    def draft(self, headers, fn):
        '''
    
        Args:
            headers (dict): 
    
        Returns:
            dict
    
        '''
        if headers and not fn:
            url = 'https://api.playdraft.com/v1/window_clusters/2015/complete_contests'
            self.headers = headers
            return self.get_json(url=url)
        elif fn and not headers:
            return self._json_file(fn)
        else:
            raise ValueError('Must pass headers or fn')


if __name__ == "__main__":
    pass
