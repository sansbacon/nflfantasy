from nfl.scrapers.scraper import FootballScraper


class FFNerdNFLScraper(FootballScraper):

    '''
    Obtains content of NFL fantasy projections page of fantasyfootballnerd.com
    Content will be a dictionary of projections and rankings
    Rankings are not position specific, projections are position-specific
    So structure will be rankings: [list of players], projections: {position: [list of players]}

    Example:
        s = FFNerdNFLScraper(api_key=os.environ.get('FFNERD_API_KEY'))
        content = s.get_projections()
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

if __name__ == "__main__":
    pass