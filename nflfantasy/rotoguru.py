import logging
import re

from bs4 import BeautifulSoup

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):
    '''
    Scrape rotoguru pages

    '''
    def dfs_week(self, season_year, week, site):
        '''
        Gets rotoguru page of one week of dfs results - goes back to 2014

        Args:
            season_year(int): 2016, 2015, etc.
            week(int): 1-17
            site(str): 'dk', 'fd', etc.

        Returns:
            str - HTML

        '''
        sites = ['dk', 'fd', 'yh']
        if site not in sites:
            raise ValueError('invalid site: {}'.format(site))
        url = 'http://rotoguru1.com/cgi-bin/fyday.pl?'
        params = {'week': week, 'year': season_year, 'game': site, 'scsv': 1}
        return self.get(url, params=params)


class Parser():
    '''
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def dfs_week(self, content):
        '''
        Parses weekly dfs results (ssv content wrapped by <pre>)

        Args:
            content:

        Returns:

        '''
        vals = []
        soup = BeautifulSoup(content, 'lxml')
        for pre in soup.findAll('pre'):
            if 'Week;Year' in pre.text:
                rows = pre.text.split('\n')
                headers = [item.strip().lower().replace(' ', '_').replace('/', '')
                           for item in rows[0].split(';')]
                for row in rows[1:]:
                    sal = dict(list(zip(headers, row.split(';'))))
                    if sal.get('salary', None):
                        sal['salary'] = re.sub("[^0-9]", "", sal['salary'])
                    vals.append(sal)
        return vals


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()

    def dfs_week(self, season_year, week, site):
        '''

        Args:
            season_year(int): 2015 -
            week(int): 1-17
            site(str): 'dk', 'fd'

        Returns:
            str - HTML

        '''
        content = self._s.dfs_week(season_year, week, site)
        return self._p.dfs_week(content)


if __name__ == '__main__':
    pass
