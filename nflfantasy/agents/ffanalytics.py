import logging
import os
import pprint

from nfl.db import nflpg
from nfl.parsers import ffanalytics


class FantasyFootballAnalyticsNFLAgent(object):
    '''
    Usage:

    '''

    def __init__(self, fn):
        self._p = ffanalytics.FantasyFootballAnalyticsParser()
        self._npg = nflpg.NFLPostgres(user=os.environ.get('NFLPGUSER'), password=os.environ.get('NFLPGPASSWORD'), 
		database=os.environ.get('NFLPGDB'))
        self._fn = fn

    def weekly_dk_projections(self, season, week):
        '''
        Gets dk projections, merges with salary data (ffanalytics does not have salaries)

        Returns:
            players(list): of player dict
        '''

        # cross-reference site_player_id with player_id
        q = '''SELECT site_player_id, player_id FROM player_xref WHERE site = 'ffanalytics';'''
        player_xref = {p['site_player_id']: p['player_id'] for p in self._npg.select_dict(q)}

        # get salaries linked to player_id
        q = '''SELECT player_id, salary FROM salaries WHERE season = 2016 AND week = 2;'''
        player_sal = {p.get('player_id', 'N/A'): p.get('salary', None) for p in self._npg.select_dict(q)}

        # now merge salary data with projections data
        # columns 'playerId', 'Name', 'Position', 'teamAbbrev', 'AvgPointsPerGame', 'median', 'upper', 'lower', 'risk']
        players = self._p.weekly_dk_projections(self._fn, dk_format=True)
        for idx, player in enumerate(players):
            spid = str(player.get('site_player_id'))
            if spid:
                pid = player_xref.get(spid)
                if pid:
                    players[idx]['player_id'] = pid
                    players[idx]['Salary'] = player_sal.get(pid, None)
                else:
                    logging.error('player {}: could not find player_id for {}, {}'.format(idx, player.get('Name'), spid))

            else:
                logging.error('player {}: could not find site_player_id for {}'.format(idx, player.get('Name')))

        return players

if __name__ == '__main__':
    import pandas as pd

    logging.basicConfig(level=logging.DEBUG)
    fn = '/home/sansbacon/Downloads/FFA-CustomRankings.csv'
    a = FantasyFootballAnalyticsNFLAgent(fn)
    players = a.weekly_dk_projections(2016, 2)
    df = pd.DataFrame(players)
    df.to_csv('~/w2projections.csv', index=False)
