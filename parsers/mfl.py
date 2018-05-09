# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging

from bs4 import BeautifulSoup


class MFLParser(object):
    '''
    Parses xml from myfantasyleague.com API
    
    Example:
        p = MyFantasyLeagueNFLParser()
        players = p.players(content)
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def players (self, content):
        '''
        Parses xml and returns list of player dictionaries
        
        Args:
            content (str): xml typically fetched by Scraper class
        
        Returns:
            List of dictionaries if successful, empty list otherwise.
        '''
        soup = BeautifulSoup(content, 'xml')
        return [{att: p[att] for att in p.attrs} for p in soup.find_all('player')]

if __name__ == '__main__':
    pass