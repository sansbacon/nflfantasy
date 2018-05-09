from nfl.scrapers.scraper import FootballScraper


class FantasyFootballCalculatorScraper(FootballScraper):
    '''
    Obtains html content of NFL fantasy projections or ADP page of fantasycalculator.com       
    '''

    def adp(self, fmt='ppr', teams=12):
        '''
        Gets ADP page from fantasyfootballcalculator        

        Args:
            fmt: 
            teams: 

        Returns:
            HTML string or None
        '''
        url = 'https://fantasyfootballcalculator.com/adp_xml.php?'
        params = {'format': fmt, 'teams': teams}
        return self.get(url, payload=params)

    def adp_old(self, season_year, fmt='ppr'):
        '''
        Gets ADP page from fantasyfootballcalculator        

        Args:
            fmt: 
            teams: 

        Returns:
            HTML string or None
        '''
        url = 'https://fantasyfootballcalculator.com/adp?'
        params = {'year': season_year, 'format': fmt, 'teams': '12', 'view': 'graph', 'pos': 'all'}
        return self.get(url, payload=params)

    def projections(self):
        '''
        Fetch projections/rankings

        Args:
            url (str): url for the fantasy football calculator projections page

        Returns:
            HTML string if successful, None otherwise.
        '''
        url = 'https://fantasyfootballcalculator.com/rankings'
        return self.get(url)

if __name__ == "__main__":
    pass