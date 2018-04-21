'''
RotoguruNFLScraper

'''

import logging

from nfl.scrapers.scraper import FootballScraper


class RotoguruNFLScraper(FootballScraper):
    '''

    '''

    def dfs_week(self, season_year, week, site):
        '''
        Gets rotoguru page of one week of dfs results - goes back to 2014

        Args:
            season_year: int 2016, 2015, etc.
            week: int 1-17
            site: 'dk', 'fd', etc.

        Returns:
            HTML string
        '''
        sites = ['dk', 'fd', 'yh']
        if site not in sites:
            raise ValueError('invalid site: {}'.format(site))
        url = 'http://rotoguru1.com/cgi-bin/fyday.pl?'
        params = {'week': week, 'year': season_year, 'game': site, 'scsv': 1}
        return self.get(url, payload=params)

if __name__ == "__main__":
    pass
