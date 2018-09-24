# -*- coding: utf-8 -*-

import json

from nflmisc.scraper import FootballScraper


class DraftNFLScraper(FootballScraper):
    '''
    '''

    def _json_file(self, fn):
        '''
        Opens JSON file from disk

        Args:
            fn:

        Returns:
            dict: JSON parsed into dict

        '''
        with open(fn, 'r') as infile:
            return json.load(infile)

    def adp(self, start_date, end_date, season_year, participants, entry_cost, token):
        '''

        Args:
            start_date:
            end_date:
            season_year:
            participants:
            entry_cost:
            token:

        Returns:
            dict

        '''
        url = 'https://api.playdraft.com/feeds/v2/sports/nfl//season/adp?'
        params = {'start_date': start_date,
                  'end_date': end_date,
                  'year': season_year,
                  'participants': participants,
                  'entry_cost': entry_cost,
                  'token': token}
        return self.get_json(url, params)

    def complete_contests(self, fn=None):
        '''

        Args:
            fn (str):

        Returns:
            dict

        '''
        if fn:
            return self._json_file(fn)
        else:
            url = 'https://api.playdraft.com/v1/window_clusters/2015/complete_contests'
            return self.get_json(url=url)

    def draft(self, league_id=None, fn=None):
        '''

        Args:
            league_id (str):
            fn (str):

        Returns:
            dict

        '''
        if fn:
            return self._json_file(fn)
        elif league_id:
            url = 'https://api.playdraft.com/v3/drafts/{}'
            return self.get_json(url=url.format(league_id))
        else:
            return ValueError('must specify league_id or fn')

    def player_pool(self, pool_id=None, fn=None):
        '''

        Args:
            fn (dict):

        Returns:
            dict

        '''
        if fn:
            return self._json_file(fn)
        elif pool_id:
            url = 'https://api.playdraft.com/v4/player_pool/{}'
            return self.get_json(url.format(pool_id))
        else:
            return ValueError('must specify pool_id or fn')


if __name__ == "__main__":
    pass

