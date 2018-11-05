# -*- coding: utf-8 -*-

from csv import reader
import datetime
import json
import logging
import mmap
import re

import pandas as pd

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''
    TODO: this class is not really implemented. Need to add in the contest page stuff as well.
    '''

    def __init__(self):
        self.contest_fn = None

    def draft_groups(self, dgid, compid):
        '''
        Gets dk draft group

        Args:
            dgid(int): dk draftgroup id
            compid(int): dk competition id

        Returns:
            dict: parsed JSON

        '''
        base_url = ('https://api.draftkings.com/draftgroups/v2/draftgroups/{}/'
                    'competitions/{}/depthchart?format=json')
        return self.get_json(base_url.format(dgid, compid))

    def contest_data(self, fname):
        '''
        Uses memory map instead of file_io to process DK contest results

        Args:
            fname: string

        Returns:
            memory map of file
        '''
        try:
            with open(fname, 'r+b') as f:
                return mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        except Exception as e:
            logging.exception(e)

    def _entry(self, line, contest_id):

        entry = {'contest_id': contest_id}

        fields = [x.strip() for x in line.split(',')]

        entry['contest_rank'] = fields[0]
        entry['entry_id'] = fields[1]

        # entries is in format: ScreenName (entryNumber/NumEntries)
        if '(' in fields[2]:
            name, entries = [x.strip() for x in fields[2].split(' ')]
            entry['entry_name'] = name

            match = re.search(r'\d+/(\d+)', entries)
            if match:
                entry['num_entries'] = match.group(1)

        else:
            entry['entry_name'] = fields[2]
            entry['num_entries'] = 1

        # fantasy points scored
        entry['points'] = fields[4]

        # parse lineup_string into lineup dictionary, add to entry
        lineup_string = fields[5]
        lineup = self._lineup(lineup_string)
        for position in lineup:
            entry[position] = lineup[position]

        return entry

    def _lineup(self, lineup_string):

        lineup = {}
        pattern = re.compile(
            r'QB\s+(?P<qb>.*?)\s+RB\s+(?P<rb1>.*?)\s+RB\s+(?P<rb2>.*?)\s+WR\s+(?P<wr1>.*?)\s+WR\s+('
            r'?P<wr2>.*?)\s+WR\s+(?P<wr3>.*?)\s+TE\s+(?P<te>.*?)\s+FLEX (?P<flex>.*?) DST(?P<dst>.*?)')

        if ',' in line:
            fields = [x.strip() for x in line.split(',')]
            lineup_string = fields[-1]

            match = re.search(pattern, lineup_string)
            if match:
                lineup = match.groupdict()

                # can't seem to get last part of regex to work
                if 'dst' in lineup and lineup['dst'] == '':
                    parts = lineup_string.split(' ')
                    lineup['dst'] = parts[-1]
                    parts = lineup_string.split(' ')
                    lineup['dst'] = parts[-1]

            else:
                root.debug('missing lineup_string')

        return lineup

    def salary_data(self, fname):

        try:
            df = pd.read_csv(fname, header=True)
        except:
            logging.exception('salary_data(fname): fname must exist')


class Parser():
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _team_id_to_code(self, id):
        d = {324: 'BUF', 325: 'HOU', 326: 'CHI', 327: 'CIN', 329: 'CLE', 331: 'DAL',
             332: 'DEN', 334: 'DET', 335: 'GB', 336: 'TEN', 338: 'IND', 339: 'KC',
             341: 'OAK', 343: 'LAR', 345: 'MIA', 347: 'MIN', 348: 'NE', 350: 'NO',
             351: 'NYG', 354: 'PHI', 355: 'ARI', 356: 'PIT', 357: 'LAC', 359: 'SF',
             361: 'SEA', 362: 'TB', 363: 'WAS', 364: 'CAR', 365: 'JAX', 366: 'BAL'}
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
                pos = posdepth.get('positionAbbreviation')
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

    def lobby(self, content, season, week):
        '''
        Parses dk lobby (json embedded in HTML page) and returns list of contest dicts

        Args:
            content(str): HTML from lobby
            season (int):
            week (int): for football only

        Returns:
            contests(list): of contest dicts
        '''
        contests = []
        pattern = re.compile(r'packagedContests = (\[.*?\])\;', re.MULTILINE | re.DOTALL)
        match = re.search(pattern, content)

        if match:
            for contest in json.loads(match.group(1)):
                # 1 - NFL, 2- MLB, NBA??
                if contest.get('s') == 1:
                    # convert epoch string to date
                    ds = re.findall('\d+', contest.get('sd', ''))[0]
                    cd = datetime.datetime.strftime(datetime.datetime.fromtimestamp(float(ds) / 1000), '%m-%d-%Y')

                    # create context dict
                    headers = ['season', 'week', 'contest_name', 'contest_date', 'contest_slate', 'contest_fee',
                               'contest_id', 'max_entries', 'contest_size', 'prize_pool']
                    vals = [season, week, contest.get('n'), cd, contest.get('sdstring'), contest.get('a'),
                            contest.get('id'), contest.get('mec'), contest.get('m'), contest.get('po')]
                    contests.append(dict(zip(headers, vals)))

        return contests

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
        players = [{k: v for k, v in p.items() if k in wanted} for p in content['playerList']]
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
