# -*- coding: utf-8 -*-
# nflfantasy/pff_fantasy.py
# scraper/parser for profootballfocus.com fantasy resources

import logging
import re

from bs4 import BeautifulSoup

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''
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


class Parser():
    '''
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _name(self, player):
        try:
            return '{} {}'.format(player['first_name'], player['last_name'])
        except:
            return None

    def bestball_rankings(self, content):
        '''
        Parses pff bestball json document

        Args:
            content(dict): parsed json

        Returns:
            list: of dict

        '''
        results = []

        # teams
        teams = content['teams']
        teams_d = {t['franchise_id']: t for t in teams}

        # ranking_type
        positions = content['ranking_type']['allowed_positions']
        ranking_type = content['ranking_type']['path']
        season = content['ranking_type']['season']

        # rankers
        rankers = content['rankers']
        rankers_d = {r['id']: r for r in rankers}

        # players
        players = content['players']
        players_d = {p['player_id']: p for p in players}

        # position_rankings
        for posrank in content['position_rankings']:
            pos = posrank['position']
            for prkg in posrank['player_rankings']:
                pid = prkg['player_id']
                for rnk in prkg['ranks']:
                    results.append({'source_player_id': pid,
                                    'source_player_name': self._name(players_d.get(pid)),
                                    'source_player_rank': rnk['rank'],
                                    'source_ranker_id': rnk['ranker_id'],
                                    'source_ranker_name': rankers_d[rnk['ranker_id']]['name'],
                                    'source_player_position': pos,
                                    'season_year': season, 'source_ranking_type': ranking_type})

        # players
        # all_ranking_types

        return results


    def weekly_projections(self, content):
        '''
        Parses profootballfocus weekly projections

        Args:
            content(dict): parsed JSON

        Returns:
            list

        '''
        return content['player_projections']


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()

    def weekly_projections(self, week):
        '''
        Gets PFF weekly projections

        Args:
            week(int):

        Returns:
            list: of dict

        '''
        content = self._s.weekly_projections(week)
        return self._p.weekly_projections(content)


if __name__ == '__main__':
    pass
