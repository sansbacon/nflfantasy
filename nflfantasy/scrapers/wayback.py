# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division

import logging

from nfl.dates import convert_format, subtract_datestr, today
from nfl.scrapers.scraper import FootballScraper


class WaybackScraper(FootballScraper):


    def __init__(self, headers=None, cookies=None, cache_name=None, expire_hours=12, as_string=False):
        '''
        Scraper for waybackmachine API

        Args:
            headers: dictionary of HTTP headers
            cookies: cookie object, such as browsercookie.firefox()
            cache_name: str 'nbacomscraper'
            expire_hours: how long to cache requests
            as_string: return as raw string rather than json parsed into python data structure
        '''
        FootballScraper.__init__(self, headers, cookies, cache_name, expire_hours, as_string)
        self.wburl = 'http://archive.org/wayback/available?url={}&timestamp={}'

    def get_wayback(self, url, d=None, max_delta=None):
        '''
        Gets page from the wayback machine
        Args:
            url: of the site you want, not the wayback machine
            d: datestring, if None then get most recent one
            max_delta: int, how many days off can the last page be from the requested date
        Returns:
            content: HTML string
        '''
        content = None
        ts = None

        if not d:
            d = today('db')
        else:
            d = convert_format(d, 'db')
        resp = self.get_json(self.wburl.format(url, d))

        if resp:
            try:
                ts = resp['archived_snapshots']['closest']['timestamp'][:8]
                if ts and max_delta:
                    closest_url = resp['archived_snapshots']['closest']['url']
                    if abs(subtract_datestr(d, ts)) <= max_delta:
                        content = self.get(resp['archived_snapshots']['closest']['url'])
                    else:
                        logging.error('page is too old: {}'.format(ts))
                else:
                    closest_url = resp['archived_snapshots']['closest']['url']
                    content = self.get(closest_url)

            except Exception as e:
                logging.exception(e)
        else:
            logging.error('url unavailable on wayback machine')

        return content, ts

if __name__ == "__main__":
    pass