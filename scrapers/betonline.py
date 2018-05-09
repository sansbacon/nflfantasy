# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

from nfl.scrapers.scraper import FootballScraper


class BetOnlineNFLScraper(FootballScraper):
    '''

    '''

    def lines(self):
        '''
        Gets xml feed from betonline.com
        '''
        url = 'http://livelines.betonline.com/sys/LineXML/LiveLineObjXml.asp?sport=Football'
        return self.get(url)

if __name__ == "__main__":
    pass
