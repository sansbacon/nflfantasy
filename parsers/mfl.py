# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging


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


if __name__ == '__main__':
    pass