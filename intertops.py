import logging
import re

from bs4 import BeautifulSoup

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''
    def __init__(self, api_key, response_format='json',
                 headers=None, cookies=None, cache_name=None,
                 delay=1, expire_hours=168, as_string=False):
        '''
        Scrape intertops API

        Args:
            api_key: string
            response_format: json or xml
            headers: dict of headers
            cookies: cookiejar object
            cache_name: should be full path
            delay: int (be polite!!!)
            expire_hours: int - default 168
            as_string: get string rather than parsed json

        '''
        FootballScraper.__init__(self, headers, cookies, cache_name, delay, expire_hours, as_string)
        self.api_key = api_key
        self.response_format = response_format

    def categories(self):
        """
        Gets categories from intertops

        Returns:
            dict

        """
        url = 'http://xmlfeed.intertops.com/xmloddsfeed/v2/{fmt}/categoryfeed.ashx'
        params = {'apikey': self.api_key, 'sportId': 1}
        return self.get_json(url.format(fmt=self.response_format, api_key=self.api_key), payload=params)

    def odds(self, delta=14400):
        """
        Gets odds from intertops
        Have to be careful with delta parameter because could miss info otherwise but, if poll too often,
        site TOS states that it may revoke your API key.

        Args:
            delta: int, number of minutes since last update. You need to be careful with this per site TOS.

        Returns:
            dict

        """
        url = 'http://xmlfeed.intertops.com/xmloddsfeed/v2/{fmt}/feed.ashx'
        params = {'apikey': self.api_key, 'sportId': 1}
        return self.get_json(url.format(fmt=self.response_format, api_key=self.api_key), payload=params)


class Parser():
    '''
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())



class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()



if __name__ == '__main__':
    pass
