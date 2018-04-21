# -*- coding: utf-8 -*-

import logging
import re
import sys
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

import pandas as pd


class FantasyFootballAnalyticsParser(object):
    '''
    Parses csv of NFL fantasy projections page of fantasyfootballanalytics.com into player dictionaries

    Usage:
        p = FantasyFootballAnalyticsParser()
        players = p.weekly_dk_projections(fn='/home/sansbacon/Downloads/FFA-CustomRankings.csv')
        players = p.weekly_dk_projections(fn='/home/sansbacon/Downloads/FFA-CustomRankings.csv', dk_format=False)
    '''

    def weekly_dk_projections(self, fn, dk_format=True):
        '''
        Args:
            fn (str): path to csv file
        Returns:
            players(list): of player dictionaries
        '''

        players = []

        # the FFAnalytics file has an extra comma at the end of each line, want to remove
        with open(fn, 'r') as infile:
            content = infile.read()

        try:
            # headers: playerId, player, playername, position, team, playerposition, playerteam, vor, points, actualPoints,
            # overallECR, overallRank, positionRank, cost, salary, dropoff, adp, adpdiff, auctionValue, upper, lower, risk, sleeper

            wanted = ['playerId', 'playername', 'position', 'team', 'points', 'upper', 'lower', 'risk']
            csv = StringIO(re.sub(r',(\s+)', r'\1', content))
            df = pd.read_csv(csv, index_col=None, usecols=wanted)
            if dk_format:
                df['median'] = df['points']
                df.rename(columns={'playername': 'Name', 'position': 'Position', 'team': 'teamAbbrev',
                                   'points': 'AvgPointsPerGame', 'playerId': 'site_player_id'}, inplace=True)

            players = df.T.to_dict().values()

        except:
            logging.exception('could not parse csv file')

        finally:
            return players

if __name__ == '__main__':
    pass
