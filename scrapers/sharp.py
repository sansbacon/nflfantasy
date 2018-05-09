# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

from nfl.scrapers.scraper import FootballScraper


class SharpScraper(FootballScraper):
    '''

    '''

    def odds(self):
        '''
        Gets odds data from sharpfootball
        
        Returns:
            XML string
        '''
        url = 'http://www.sharpfootballanalysis.com/schedule.php?host=SHARPFB&sport=nfl&period=0'
        return self.get(url)

if __name__ == "__main__":
    pass
