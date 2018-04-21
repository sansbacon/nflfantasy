# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division
import logging

from nfl.scrapers.scraper import FootballScraper


class FFTodayScraper(FootballScraper):
    '''
    Scrapes fftoday.com pages
    '''

    def position_id(self, pos):
        '''
        
        Args:
            pos: 'qb', 'rb', etc.

        Returns:
            int 10, 20, etc.
        '''
        return {'qb': 10, 'rb': 20, 'wr': 30, 'te': 40, 'dst': 99, 'def': 99, 'k': 80}.get(pos.lower(), None)

    def weekly_results(self, season, week, pos):
        '''
        Scrapes weekly results from fftoday.com

        Args:
            season: 2016, 2015, etc.
            week: 1, 2, etc.
            pos: 'QB', 'RB', etc.

        Returns:
            HTML string if successful, None otherwise.
        '''
        url = 'http://fftoday.com/stats/playerstats.php?'
        params = {'Season': season, 'GameWeek': week, 'PosID': self.position_id(pos), 'LeagueID': '107644'}
        return self.get(url, payload=params)

    def weekly_rankings(self, season, week, pos):
        '''
        Fetch projections/rankings

        Args:
            season: 2016, 2015, etc.
            week: 1, 2, etc.
            pos: 'QB', 'RB', etc.

        Returns:
            HTML string if successful, None otherwise.
        '''
        if pos.lower() in ['qb', 'rb']:
            pos_id = 10
        elif pos.lower() in ['wr', 'te']:
            pos_id = 30
        elif pos.lower() in ['def', 'k']:
            pos_id = 80
        else:
            raise ValueError('invalid position: {}'.format(pos))

        url = 'https://fftoday.com/rankings/playerwkrank.php?'
        params = {'Season': season, 'GameWeek': week, 'PosID': pos_id}
        return self.get(url, payload=params)


if __name__ == "__main__":
    pass