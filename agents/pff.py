from __future__ import print_function

import csv
import logging
from random import choice, uniform
import time

from nfl.scrapers.pff import PffNFLScraper
from nfl.parsers.pff import PffNFLParser


class PffNFLAgent():
    '''

    Usage:
        # to access paid stats, you will need a cookie library
        import browsercookie

        # uses cache to reduce API calls
        a = FantasyLabsNFLAgent(cache_name='/home/sansbacon/.rcache/fantasylabs-nfl2', cj=browsercookie.firefox())

        # get list of players with projections
        players = a.model('1_4_2017', 'levitan', 'dk')

        # optimize
        for l in a.optimize(players=players, projection_formula='cash'):
            print ('Iteration {}-{}'.format(l['iteration_id'], l['team_id']))
            print(l['players'])
    '''


    def __init__(self, cache_name='pff-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._p = PffNFLParser()
        self._s = PffNFLScraper(cache_name=cache_name)

    def weekly_projections(self, week):
        '''
        Gets PFF weekly projections

        Args:
            week(int):

        Returns:
            list: of dict

        '''
        content = self._s.weekly_projections(week)
        return self._p.weekly_projections(content)


if __name__ == '__main__':
    pass
