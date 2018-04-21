from nfl.scrapers.scraper import FootballScraper


class MFLScraper(FootballScraper):
    '''
    '''

    def players(self, season_year):
        '''
        Gets list of players from myfantasyleague.com
        
        Returns:
            HTML string
        '''
        url = 'http://football.myfantasyleague.com/{}/export?TYPE=players&DETAILS=1'
        return self.get(url.format(season_year))

if __name__ == "__main__":
    pass