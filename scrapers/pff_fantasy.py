# -*- coding: utf-8 -*-

from nflmisc.scraper import FootballScraper


class PFFScraper(FootballScraper):

    def bestball(self):
        '''
        Gets profootballfocus teams

        Returns:
            dict

        '''
        return self.get_json('https://www.profootballfocus.com/api/prankster/rankings/nfl-best-ball')

    def weekly_projections(self, week):
        '''
        Gets profootballfocus weekly projections

        Args:
            week(int): NFL week, 1-17

        Returns:
            dict

        '''
        url = 'https://www.profootballfocus.com/api/prankster/projections?'
        params = {'scoring': 54574, 'weeks': week}
        return self.get_json(url, payload=params)


if __name__ == '__main__':
    pass

    """
    import nflfantasy.scrapers.pff_fantasy as pff
    import nflfantasy.parsers.pff_fantasy as pffp

    week = 8
    s = pff.PFFScraper()
    p = pffp.PFFFantasyParser()
    proj = p.weekly_projections(s.weekly_projections(week))
    [p for p in proj if p['position'] == 'dst'][0]

    """
