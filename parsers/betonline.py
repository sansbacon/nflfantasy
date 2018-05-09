# -*- coding: utf-8 -*-

import logging

from bs4 import BeautifulSoup


class BetOnlineNFLParser(object):


    def __init__(self):
        '''
        
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def lines(self, content):
        '''

        Args:
            content (str): HTML string from espn waiver wire page

        Returns:
            dict
        '''
        games = []
        soup = BeautifulSoup(content, 'xml')
        for ev in soup.find_all('event'):
            league = ev.find('league')
            if league and league.text == 'NFL Football':
                games.append(ev)
        return games

if __name__ == "__main__":
    pass