import copy
import json
import logging

from bs4 import BeautifulSoup


class RotowireNFLParser():
    '''
    RotoguruNFLParser

    Usage:


    '''

    def __init__(self,**kwargs):
        '''

        '''

        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def dfs_week(self, dfs_site, season, week, content):
        players = []
        headers = ['player', 'pos', 'team', 'opp', 'salary', 'curr_points', 'curr_value', 'last_points', 'last_value']
 
        for tr in t.find('tbody', {'id': 'players'}).findAll('tr')[:-1]:
               
            player = dict(zip(headers, [td.text.strip() for td in tr.findAll('td')[:-1]]))
            player['source'] = 'rotowire'
            player['dfs_site'] = site
            player['season'] = season
            player['week'] = week
            player['source_player_id'] = tr['data-playerid']
            player['salary'] = re.sub('[^0-9]', '', player.get('salary'))
            
            if '\n' in player.get('player'):
                player['player'] = player['player'].split('\n')[0]
            
            players.append(player)

        return players
        
if __name__ == "__main__":
    pass
