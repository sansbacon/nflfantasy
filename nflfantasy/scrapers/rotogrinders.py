import json

from nfl.scrapers.browser import BrowserScraper


class RotoGrindersNFLScraper(BrowserScraper):
    '''
    '''

    def projections(self, site, pos):
        '''
        Gets weekly projections for position group
        
        Args:
            site: 'draftkings', 'fanduel' 
            pos:  'qb', 'rb', etc.

        Returns:
            parsed JSON
        '''
        if site == 'dk' or 'king' in site:
            site = 'draftkings'
        elif site == 'fd' or 'duel' in site:
            site = 'fanduel'
        else:
            raise ValueError('invalid site: {}'.format(site))

        if pos in ['qb', 'QB', 'rb', 'RB', 'wr', 'WR', 'te', 'TE']:
            pos = pos.lower()
        elif pos in ['dst', 'DST', 'defense', 'D', 'D/ST', 'def']:
            pos = 'defense'
        else:
            raise ValueError('invalid position: {}'.format(pos))

        # data is in javascript variable
        # can use execute script to get stringified version, then load with json.loads
        pos = pos.lower()
        url = 'https://rotogrinders.com/projected-stats/nfl-{}?site={}'
        self.browser.get(url)
        result = self.browser.execute_script("return JSON.stringify(projectedStats.data);")
        return json.loads(result)


    def slates(self, site, pos='qb'):
        '''
        Gets site slate information
        
        Args:
            site: 'draftkings', 'fanduel' 
            pos:  'qb', 'rb', etc.

        Returns:
            parsed JSON
        '''
        if site == 'dk' or 'king' in site:
            site = 'draftkings'
        elif site == 'fd' or 'duel' in site:
            site = 'fanduel'
        else:
            raise ValueError('invalid site: {}'.format(site))

        if pos in ['qb', 'QB', 'rb', 'RB', 'wr', 'WR', 'te', 'TE']:
            pos = pos.lower()
        elif pos in ['dst', 'DST', 'defense', 'D', 'D/ST', 'def']:
            pos = 'defense'
        elif pos in ['k', 'K', 'kicker', 'Kicker']:
            pos = 'kicker'
        else:
            raise ValueError('invalid position: {}'.format(pos))

        # data is in javascript variable
        # can use execute script to get stringified version, then load with json.loads
        url = 'https://rotogrinders.com/projected-stats/nfl-{}?site={}'
        self.browser.get(url)
        result = self.browser.execute_script("return JSON.stringify(window.slateSelect);")
        return json.loads(result)


if __name__ == "__main__":
    pass