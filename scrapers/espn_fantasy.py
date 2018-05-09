# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import re

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

from nfl.dates import today, yesterday_x
from nfl.scrapers.browser import BrowserScraper
from nfl.seasons import current_season_year


class ESPNFantasyScraper(BrowserScraper):
    '''
    '''

    def __init__(self, config, visible=False, profile=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        BrowserScraper.__init__(self, visible=visible, profile=profile)
        self.user = config.get('espn', 'username')
        self.password = config.get('espn', 'password')

    def drops(self, league_id, season_year=None, start_date=None, end_date=None):
        '''
        http://games.espn.com/ffl/recentactivity?

        Args:
            league_id: 

        Returns:

        '''
        if not start_date:
            start_date = yesterday_x(interval=2, fmt='espn_fantasy')
        if not end_date:
            end_date = today(fmt='espn_fantasy')
        if not season_year:
            season_year = current_season_year()

        url = 'http://games.espn.com/ffl/recentactivity'
        params = {
            'leagueId': league_id,
            'activityType': '2',
            'startDate': start_date,
            'seasonId': season_year,
            'endDate': end_date,
            'teamId': '-1',
            'tranType': '3'
        }

        url = '{}?{}'.format(url, urlencode(params))
        driver = self.browser
        driver.get(url)
        self.urls.append(url)
        return self.browser.page_source

    def fantasy_league_rosters(self, league_id, encoding='latin1'):
        '''
        Gets roster for team in ESPN fantasy league
        '''
        url = 'http://games.espn.com/ffl/leaguerosters'
        params = {'leagueId': league_id}
        url = '{}?{}'.format(url, urlencode(params))
        driver = self.browser
        driver.get(url)
        self.urls.append(url)
        return self.browser.page_source

    def fantasy_league_scoreboard(self, league_id, season):
        '''
        Gets scoreboard from ESPN fantasy league
        '''
        params = {'leagueId': league_id, 'seasonId': season}
        url = 'http://games.espn.com/ffl/scoreboard?{}'.format(urlencode(params))
        driver = self.browser
        driver.get(url)
        self.urls.append(url)
        return self.browser.page_source

    def fantasy_team_roster(self, league_id, team_id, season):
        '''
        Gets roster for team in ESPN fantasy league
        '''
        params = {'leagueId': league_id,
                      'teamId': team_id,
                      'seasonId': season}
        url = 'http://games.espn.com/ffl/clubhouse?{}'.format(urlencode(params))
        driver = self.browser
        driver.get(url)
        self.urls.append(url)
        return self.browser.page_source

    def fantasy_projections(self, offset=0):
        '''
        Gets ESPN fantasy football projections
        '''
        url = 'http://games.espn.go.com/ffl/tools/projections?'
        params = {'startIndex': offset}
        return self.get(url, payload=params)

    def fantasy_waiver_wire(self, league_id, team_id, season, start_index=None, position=None):
        '''
        Gets waiver wire from ESPN fantasy league
        league_id=488173, team_id=12, season=2017
        '''
        slot_categories = {
            'qb': 0,
            'rb': 2,
            'wr': 4,
            'te': 6,
            'dst': 16,
            'k': 17
        }
        params = {'leagueId': league_id, 'teamId': team_id, 'seasonId': season}
        if start_index:
            if start_index not in [0, 50, 100, 150, 200]:
                raise ValueError('start index invalid: {}'.format(start_index))
            params['startIndex'] = start_index
        if position:
            params['slotCategoryId'] = slot_categories[position.lower()]
        url = 'http://games.espn.com/ffl/freeagency?' + urlencode(params)
        self.browser.get(url)
        self.urls.append(url)
        return self.browser.page_source

if __name__ == "__main__":
    pass