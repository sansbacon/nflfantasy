# -*- coding: utf-8 -*-

import json


class PFFFantasyParser(object):

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


if __name__ == '__main__':
    pass