import logging

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''

    def __init__(self, api_key, response_format='json', league_format='1',
                 headers=None, cookies=None, cache_name=None,
                 delay=1, expire_hours=168, as_string=False):
        '''
        Scrape ffnerd API

        Args:
            api_key: string
            response_format: json or xml
            league_format: 1 for ppr, 0 for standard
            headers: dict of headers
            cookies: cookiejar object
            cache_name: should be full path
            delay: int (be polite!!!)
            expire_hours: int - default 168
            as_string: get string rather than parsed json
        '''
        FootballScraper.__init__(self, headers, cookies, cache_name, delay, expire_hours, as_string)
        self.api_key = api_key
        self.positions = ['QB', 'RB', 'WR', 'TE', 'DEF']
        self.response_format = response_format
        self.league_format = league_format

    def depth_charts(self):
        '''
        NFL team depth charts

        Returns:
            dict
        '''
        url = 'http://www.fantasyfootballnerd.com/service/depth-charts/{rformat}/{api_key}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key))

    def draft_projections(self, pos):
        '''
        Draft rankings for current season

        Args:
            pos:

        Returns:
            dict
        '''
        url = 'http://www.fantasyfootballnerd.com/service/draft-projections/{rformat}/{api_key}/{pos}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key, pos=pos))

    def draft_rankings(self):
        '''
        Draft rankings for current season

        Returns:
            dict
        '''
        url = 'http://www.fantasyfootballnerd.com/service/draft-rankings/{rformat}/{api_key}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key))

    def draft_tiers(self):
        '''
        Draft tiers for current season

        Returns:
            dict
        '''
        url = 'http://www.fantasyfootballnerd.com/service/tiers/{rformat}/{api_key}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key))

    def injuries(self, week):
        '''

        Args:
            week: int 1-17

        Returns:
            dict
        '''
        url = 'http://www.fantasyfootballnerd.com/service/injuries/{rformat}/{api_key}/{week}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key, week=week))

    def players(self, pos=None):
        '''
        Gets plalyers

        Args:
            pos: default None

        Returns:
            dict
        '''
        if pos:
            url = 'http://www.fantasyfootballnerd.com/service/players/{rformat}/{api_key}/{pos}'
            return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key, pos=pos))
        else:
            url = 'http://www.fantasyfootballnerd.com/service/players/{rformat}/{api_key}'
            return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key))

    def schedule(self):
        '''
        Gets schedule for current season

        Returns:
            dict
        '''
        url = 'http://www.fantasyfootballnerd.com/service/schedule/{rformat}/{api_key}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key))

    def weekly_projections(self, week, pos):
        '''

        Args:
            week:
            pos:

        Returns:

        '''
        if pos not in self.positions:
            raise ValueError('invalid position: {}'.format(pos))
        url = 'http://www.fantasyfootballnerd.com/service/weekly-projections/{rformat}/{api_key}/{pos}/{week}/'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key, pos=pos, week=week))

    def weekly_rankings(self, week, pos):
        '''

        Args:
            week:
            pos:

        Returns:

        '''
        if pos not in self.positions:
            raise ValueError('invalid position: {}'.format(pos))
        url = 'http://www.fantasyfootballnerd.com/service/weekly-rankings/{rformat}/{api_key}/{pos}/{week}/{lformat}'
        return self.get_json(url.format(rformat=self.response_format, api_key=self.api_key,
                                        pos=pos, week=week, lformat=self.league_format))


class Parser():
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def depth_charts(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        # dict: k (team_code): v (chart) k (pos): v(list of players)
        players = []
        charts = content.get('DepthCharts')
        for team, chart in charts.items():
            for pos, poschart in chart.items():
                for p in poschart:
                    p['source'] = 'ffnerd'
                    players.append(p)
        return players

    def draft_projections(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        return content.get('DraftProjections')

    def draft_rankings(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        wanted = ['playerId', 'displayName', 'team', 'position', 'byeWeek', 'standDev', 'nerdRank',
                  'positionRank', 'overallRank']
        return [{k: v for k, v in g.items() if k in wanted} for g in content.get('DraftRankings')]

    def draft_tiers(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        return content

    def injuries(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        players = []
        inj = content.get('Injuries')
        if inj:
            for team, injuries in inj.items():
                for p in injuries:
                    p['source_player_team'] = team
                    p['source'] = 'ffnerd'
                    players.append(p)
        return players

    def players(self, content):
        '''
        Current players

        Args:
            content: json parsed into dict

        Returns:
            list of dict
        '''
        wanted = ['playerId', 'displayName', 'team', 'position', 'dob', 'college']
        players = content.get('Players')
        logging.info(type(players))
        if players:
            return [{k: v for k, v in p.items() if k in wanted} for p in players]
        else:
            return None

    def schedule(self, content):
        '''
        Current season schedule

        Args:
            content: json parsed into dict

        Returns:
            list of dict
        '''
        wanted = ['gameId', 'gameWeek', 'gameDate', 'awayTeam', 'homeTeam']
        return [{k: v for k, v in g.items() if k in wanted} for g in content.get('Schedule')]

    def weekly_projections(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        players = []
        week = content.get('Week')
        pos = content.get('Pos')
        for p in content.get('Projections'):
            p['week'] = week
            p['source_player_position'] = pos
            p['source'] = 'ffnerd'
            players.append(p)
        return players

    def weekly_rankings(self, content):
        '''

        Args:
            content:

        Returns:

        '''
        players = []
        for p in content.get('Rankings'):
            p['source_player_position'] = p['position']
            p.pop('position', None)
            p['source'] = 'ffnerd'
            players.append(p)
        return players


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()



if __name__ == '__main__':
    pass
