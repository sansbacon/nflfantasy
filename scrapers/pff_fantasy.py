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


if __name__ == '__main__':
    pass