'''
RotowireNFLScraper

'''

from nfl.scrapers.scraper import FootballScraper


class RotowireNFLScraper(FootballScraper):
    '''
    Usage:
        s = RotoguruNFLScraper()

    '''

    def dfs_week(self, year, week, site='DraftKings'):
        '''
        Gets rotowire page of one week of dfs results
        '''
        if site not in ['DraftKings', 'FanDuel']:
            raise ValueError('invalid site name {}'.format(site))
        url = 'http://www.rotowire.com/daily/nfl/value-report.php?site={}'
        return self.get(url.format(site))

if __name__ == "__main__":
    pass
