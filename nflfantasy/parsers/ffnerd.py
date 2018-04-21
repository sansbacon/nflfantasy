# -*- coding: utf-8 -*-

import logging


class FFNerdNFLParser(object):

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
        return [{k:v for k,v in g.items() if k in wanted} for g in content.get('DraftRankings')]

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
            return [{k:v for k,v in p.items() if k in wanted} for p in players]
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
        return [{k:v for k,v in g.items() if k in wanted} for g in content.get('Schedule')]

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

if __name__ == "__main__":
    pass
