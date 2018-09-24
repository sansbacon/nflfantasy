# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

from csv import reader
import datetime
import json
import logging


class DraftKingsNFLParser(object):
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _team_id_to_code(self, id):
        d = {324: 'BUF',  325: 'HOU',  326: 'CHI',  327: 'CIN',  329: 'CLE',  331: 'DAL',
                 332: 'DEN',  334: 'DET',  335: 'GB',  336: 'TEN',  338: 'IND',  339: 'KC',
                 341: 'OAK',  343: 'LAR',  345: 'MIA',  347: 'MIN',  348: 'NE',  350: 'NO',
                 351: 'NYG',  354: 'PHI',  355: 'ARI',  356: 'PIT',  357: 'LAC',  359: 'SF',
                 361: 'SEA',  362: 'TB',  363: 'WAS',  364: 'CAR',  365: 'JAX',  366: 'BAL'}
        return d.get(id)

    def depth_chart(self, content):
        '''
        Parses DK depth chart

        Args:
            content: parsed JSON

        Returns:
            list: of dict

        '''
        players = []

        # tdc is list with 2 elements (one for each team)
        # each team is dict with 2 keys: teamId and depthCharts
        # each depth chart is a list with elements for each position ("QB", etc.)
        # each position is dict with keys: positionAbbreviation, positionName, teamDepthChartPlayers
        # teamDepthChartPlayers is a list of dict
        # each dict has keys: rank, playerId, firstName, lastName, shortName, playerAttributes, draftableGroupings
        # playerAttributes is list (seems empty)
        # draftableGroupings is list of dict (seems like for different slates)
        # each draftableGrouping has keys: salary, rosterPositionName, draftableRosterPositions
        # draftableRosterPositions is list of dict, each has keys: draftableId, rosterPositionId
        for t in content['teamDepthCharts']:
            tc = self._team_id_to_code(t['teamId'])
            for posdepth in t['depthCharts']:
                pos =  posdepth.get('positionAbbreviation')
                for pl in posdepth.get('teamDepthChartPlayers'):
                    sal = pl.get('draftableGroupings')[0].get('salary')
                    players.append([pl['rank'], pl['firstName'], pl['lastName'], tc, pos, sal])
        return players

    def _dk_game(self, g):
        '''
        Parses dk game description
        TODO: figure out what this does

        Args:
            g(str):

        Returns:
            dict

        Examples:
            5523905 NO @ JAX
            5523912 CHI @ CIN
            5523920 CLE @ NYG
            5523921 DAL @ SF
            5523929 TB @ MIA
            5523933 HOU @ KC
            5523937 WAS @ NE
            5523950 TEN @ GB
            5523953 CAR @ BUF
            5523957 LAR @ BAL
            5523960 IND @ SEA
            5523961 PIT @ PHI
        '''

        td = {}
        d = json.loads(g)
        for g in d['draftGroup']['games']:
            atid = g['awayTeamId']
            htid = g['homeTeamId']
            a, h = g['description'].split(' @ ')
            td[atid] = a
            td[htid] = h
        return td

    def draft_groups(self, content):
        '''
        Draft groups from contests page

        Args:
            content (str): stringified javascript variable

        Returns:
            dict

        '''
        games = []
        dg = json.loads(content)
        for g in dg['draftGroup']['games']:
            games.append([g['gameId'], g['description']])
        return games

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
