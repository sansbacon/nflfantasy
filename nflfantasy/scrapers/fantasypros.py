# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division


from nfl.scrapers.scraper import FootballScraper
from nfl.scrapers.wayback import WaybackScraper


class FantasyProsNFLScraper(FootballScraper):

    '''
    '''
    @property
    def formats(self):
        return ['std', 'ppr', 'hppr']

    @property
    def positions(self):
        return set(self.std_positions + self.ppr_positions)

    @property
    def ppr_positions(self):
        return ['rb', 'wr', 'te', 'flex', 'qb-flex']

    @property
    def std_positions(self):
        return ['qb', 'k', 'dst']

    def _construct_url(self, pos, fmt, cat):
        '''
        Creates url for rankings or projections pages

        Args:
            pos: 
            fmt: 
            cat: rankings or projections

        Returns:
            url string
        '''
        if fmt not in self.formats:
            raise ValueError('invalid format: {}'.format(fmt))

        if pos not in self.positions:
            raise ValueError('invalid format: {}'.format(fmt))

        url = 'https://www.fantasypros.com/nfl/{cat}/{pos}.php'
        if pos in self.ppr_positions:
            if fmt == 'std':
                url = 'https://www.fantasypros.com/nfl/{cat}/{pos}.php'
            elif fmt == 'ppr':
                url = 'https://www.fantasypros.com/nfl/{cat}/ppr-{pos}.php'
            elif fmt == 'hppr':
                url = 'https://www.fantasypros.com/nfl/{cat}/half-point-ppr-{pos}.php'

        return url.format(cat=cat, pos=pos)

    def adp(self, fmt):
        '''
        Gets ADP page        

        Args:
            fmt: 'std', 'ppr'

        Returns:
            content: HTML string of page
        '''
        if fmt == 'std':
            url = 'https://www.fantasypros.com/nfl/adp/overall.php'
        elif fmt == 'ppr':
            url = 'https://www.fantasypros.com/nfl/adp/ppr-overall.php'
        else:
            raise ValueError('invalid format: {}'.format(fmt))
        return self.get(url)

    def draft_rankings(self, pos, fmt):
        '''
        Gets draft rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'rankings')
        return self.get(url)

    def player_weekly_rankings(self, pid, fmt, week):
        '''
        
        Args:
            pid: 
            fmt: 
            week: 

        Returns:

        '''
        # https://www.fantasypros.com/nfl/rankings/tom-brady.php?type=weekly&week=2&scoring=PPR
        url = 'https://www.fantasypros.com/nfl/rankings/{}.php?type=weekly&week={}&scoring={}'
        return self.get(url.format(pid, week, fmt))

    def projections(self, pos, fmt, week):
        '''
        Gets rest-of-season rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'
            week: 'draft' or 1-17

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'projections')
        params = {'week': week}
        return self.get(url, payload=params)

    def ros_rankings(self, pos, fmt):
        '''
        Gets rest-of-season rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'rankings')
        url = url.replace('rankings/', 'rankings/ros-')
        return self.get(url)

    def weekly_rankings(self, pos, fmt, week=None):
        '''
        Gets weekly rankings page
        TODO: add something for the week parameter
        
        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'
            week: default None, int between 1-17

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'rankings')
        if week:
            url = '{}?week={}'.format(url, week)
        return self.get(url)

    def weekly_scoring(self, pos, params, fmt=None):
        '''
        
        Args:
            pos (str): qb, rb, etc. 

        Returns:

        '''
        if fmt:
            url = 'https://www.fantasypros.com/nfl/reports/leaders/{}-{}.php?'
            return self.get(url.format(fmt, pos.lower()), payload=params)
        else:
            url = 'https://www.fantasypros.com/nfl/reports/leaders/{}.php?'
            return self.get(url.format(pos.lower()), payload=params)


class FantasyProsWaybackNFLScraper(WaybackScraper):
    '''
    '''

    def weekly_rankings(self, pos, fmt, d):
        '''
        Gets weekly rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'
            d: datestring

        Returns:
            content: 2-element tuple with HTML string of page and datestring
        '''
        url = FantasyProsNFLScraper.construct_url(pos, fmt, 'rankings')
        return self.get_wayback(url, d)


if __name__ == "__main__":
    pass