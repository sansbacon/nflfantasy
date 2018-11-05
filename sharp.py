from collections import defaultdict
import logging
import re

from bs4 import BeautifulSoup

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''

    def odds(self):
        '''
        Gets odds data from sharpfootball

        Returns:
            str: XML string

        '''
        url = 'http://www.sharpfootballanalysis.com/schedule.php?host=SHARPFB&sport=nfl&period=0'
        return self.get(url)


class Parser():
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.positions = ['QB', 'RB', 'WR', 'TE']



class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()



if __name__ == '__main__':
    pass
