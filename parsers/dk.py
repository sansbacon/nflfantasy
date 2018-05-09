# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

from csv import reader
import datetime
import logging


class DraftKingsNFLParser(object):
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def slate_entries(self, fn):
        '''
        Parses contest download file from dk.com to get all entries

        Args:
            fn (str): filename 

        Returns:
            list: List of dict

        '''
        results = []
        with open(fn, 'r') as infile:
            # strange format in the file
            #
            for idx, row in enumerate(reader(infile)):
                if not row[0]:
                    break

                if idx == 0:
                    headers = row[0:12]
                else:
                    results.append(dict(zip(headers, row[0:12])))
        return results

    def slate_players(self, fn):
        '''
        Parses slate contest file from dk.com to get all players on slate

        Args:
            fn (str): filename 

        Returns:
            list: List of dict

        '''
        results = []
        with open(fn, 'r') as infile:
            # strange format in the file
            # data does not start until row 8 (index 7)
            for idx, row in enumerate(reader(infile)):
                if idx < 7:
                    continue
                elif idx == 7:
                    headers = row[14:21]
                else:
                    results.append(dict(zip(headers, row)))
        return results

    def weekly_contest_file(self, fn):
        '''
        Parses contest upload file from dk.com

        Args:
            fn: 

        Returns:

        '''
        results = []
        with open(fn, 'r') as infile:
            # strange format in the file
            # data does not start until row 8 (index 7)
            for idx, row in enumerate(reader(infile)):
                if idx < 7:
                    continue
                elif idx == 7:
                    headers = row[14:21]
                elif idx > 7:
                    results.append(dict(zip(headers, row[14:21])))
        return results

    def weekly_salaries_file(self, fn):
        '''
        Parses salaries file from dk.com

        Args:
            fn: 

        Returns:

        '''
        results = []
        with open(fn, 'r') as infile:
            # strange format in the file
            # data does not start until row 8 (index 7)
            for idx, row in enumerate(reader(infile)):
                if idx == 0:
                    headers = row[11:18]
                elif idx > 0:
                    results.append(dict(zip(headers, row)))
        return results


    def weekly_players_games(self, content):
        '''
        
        Args:
            content: parsed JSON dict

        Returns:
            players, games
        '''
        players = []
        wanted = ['pid', 'pcode', 'fn', 'ln', 'pn', 'tid', 'htid', 'atid', 'htabbr', 'atabbr', 's',
                  'ppg', 'or', 'pp', 'i']
        players = [{k:v for k,v in p.items() if k in wanted} for p in content['playerList']]
        games = []
        for game_id, gamev in content['teamList'].items():
            game = {'source_game_id': game_id}
            d = gamev.get('tz').split('(')[-1].split(')')[0]
            game['game_date'] = datetime.datetime.utcfromtimestamp(int(d) / 1000)
            game['source_home_team_code'] = gamev['ht']
            game['source_away_team_code'] = gamev['at']
            games.append(game)

        return players, games

if __name__ == '__main__':
    pass
