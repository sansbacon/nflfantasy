from __future__ import absolute_import, print_function, division

import logging

from nfl.dates import convert_format
from nfl.scrapers.scraper import FootballScraper
from nfl.seasons import fantasylabs_week
from nfl.utility import url_quote


class FantasyLabsNFLScraper(FootballScraper):
    '''
    FantasyLabsNFLScraper
    If you don't have a subscription, you can access the information freely-available on the website
    If you have a subscription, the scraper can use your browser cookies and access protected content
    You cannot access protected content if you (a) have not logged in (b) have the browser open
    '''

    @property
    def model_url(self):
        return 'https://www.fantasylabs.com/api/playermodel/1/{}/?modelId=1286036&projOnly=true'

    def correlations(self):
        '''
        
        Returns:

        '''
        url = 'http://api.fantasylabs.com/api/v2/correlations/views/1'
        return self.get_json(url)

    def games(self, season_year, week, fmt='fl_matchups'):
        '''
        
        Args:
            season_year: 2017, etc.
            week: 1, 2, etc.
            fmt: 'fl_matchups', 'fl2017', etc.

        Returns:

        '''
        game_date = fantasylabs_week(season_year, week, fmt)
        url = 'http://www.fantasylabs.com/api/teams/1/{}/games/'
        return self.get_json(url.format(game_date))

    def matchups(self, team_name, game_date):
        '''
        
        Args:
            game_day: 

        Returns:

        '''
        game_date = convert_format(game_date, 'fl_matchups')
        team_name = url_quote(team_name)
        url = 'http://www.fantasylabs.com/api/matchups/1/team/{}/{}'.format(team_name, game_date)
        return self.get_json(url)

    def model(self, model_day):
        '''
        Gets json for model. Stats in most models the same, main difference is the ranking based on weights.
         
        Arguments:
            model_day (str): in mm_dd_yyyy format

        Returns:
            dict
            
        '''
        self.headers = {
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9,ar;q=0.8',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
            'accept': 'application/json, text/plain, */*',
            'referer': 'https://www.fantasylabs.com/nfl/player-models/',
            'authority': 'www.fantasylabs.com',
        }

        return self.get_json(self.model_url.format(model_day))

    def sourcedata(self, game_date):
        '''
        Gets contest data
        
        Args:
            game_day: 

        Returns:
        '''
        game_date = convert_format(game_date, 'fl2017')
        url = 'http://www.fantasylabs.com/api/sourcedata/1/{}'.format(game_date)
        return self.get_json(url)

    def vegas(self, game_date):
        '''
        Gets vegas data
        
        Args:
            game_day: 

        Returns:

        '''
        game_date = convert_format(game_date, 'fl2017')
        url = 'http://www.fantasylabs.com/api/sportevents/1/{}/vegas/'.format(game_date)
        return self.get_json(url)


if __name__ == "__main__":
    pass
