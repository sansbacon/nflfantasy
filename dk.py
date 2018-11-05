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


class Agent():
    '''
    '''

    def __init__(self, cache_name=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.s = requests.Session()
        self.s.cookies = browsercookie.firefox()
        self.s.headers.update({'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'})

        if cache_name:
            requests_cache.install_cache(cache_name)
        else:
            requests_cache.install_cache(os.path.join(os.path.expanduser("~"), '.rcache', 'dk-nfl-cache'))


    def _parse_contests(self, contests):
        '''
        Gets the useful data from contest dict

        Args:
            contests(list): of contest dict

        Returns:
            parsed(list): of contest dict
        '''

        wanted = ['ContestId', 'CreatorUserId', 'DraftGroupId', 'IsDirectChallenge', 'LineupId', 'MaxNumberPlayers', 'PlayerPoints', 'Sport',
                  'TimeRemaining', 'TimeRemainingOpp', 'TotalPointsOpp', 'UserContestId', 'UsernameOpp']

        return [{k:v for k,v in c.items() if k in wanted} for c in contests]

    def live_contests(self):
        '''
        Gets list of contests

        Returns:
            contests(list): of contest dict
        '''
        r = self.s.get('https://www.draftkings.com/mycontests')
        r.raise_for_status()
        pattern = re.compile(r'live\:\s+(\[.*?\]),\s+upcoming', re.DOTALL | re.MULTILINE | re.IGNORECASE)
        match = re.search(pattern, r.content)
        if match:
            js = match.group(1)
            contests = json.loads(js)
            return self._parse_contests(contests)
        else:
            return None

    def live_hth(self):
        '''
        Gets list of live head-to-head contests (defined as MaxNumberPlayers = 2)

        Returns:
            hth(list): of contest dict
        '''
        return [c for c in self.live_contests() if c.get('MaxNumberPlayers') == 2]

    def contest_lineups(self, contest_id, user_contest_id, draft_group_id):
        '''
        Gets list of all lineups for a single DK contest
        Args:
            contest_id:
            user_contest_id:
            draft_group_id:

        Returns:
            lineups(dict):

        '''
        url = 'https://www.draftkings.com/contest/gamecenter/{}?uc={}'.format(contest_id, user_contest_id)
        r = self.s.get(url)
        r.raise_for_status()

        # contest page has var teams =
        # [{"uc":623324083,"u":725157,"un":"sansbacon","t":"(1/1)","r":1,"pmr":102,"pts":148.88},
        # {"uc":623263592,"u":1679292,"un":"Meth","t":"(1/1)","r":2,"pmr":102,"pts":132.96}]
        # need to get 'uc' to create idList parameter below
        match = re.search(r'var teams = (.*?);', r.content)

        if match:
            # contest data has the fields you need to get the lineups - not the actual lineups
            contest_data = json.loads(match.group(1))
            lineups = {int(t['uc']): {'un': t['un'], 'uc': int(t['uc']), 'pmr': t['pmr'], 'pts': t['pts']} for t in contest_data}

            # have to send POST to get lineup data (page HTML is just a stub filled in with AJAX)
            payload = {"idList":[uc for uc in lineups],"reqTs":int(time.time()),"contestId":contest_id,"draftGroupId":draft_group_id}
            r = self.s.post('https://www.draftkings.com/contest/getusercontestplayers', data=payload)
            r.raise_for_status()

            # these are the relevant fields
            # fn = first name, ln = last name, htabbr = home team abbreviation (e.g. Sea), htid = home team id (e.g. 361)
            # pcode = player code (e.g. 28887), pid = player id (e.g. 568874) NOTE: not sure what difference is
            # pn = position name, pts = fantasy points, s= salary
            # will have --, 0, or -1 as value if player is not yet locked (on opposing team)
            wanted = ['fn', 'ln', 'htabbr', 'htid', 'pcode', 'pid', 'pd', 'pn', 'pts', 's', 'tr', 'ytp']

            # want to distinguish my team vs others
            # the response is a nested dict, I want 'data' which uses the user_contest_id as its keys
            # the lineup that is mine will match the user_contest_id parameter for this method
            for ucid, team in json.loads(r.content)['data'].items():
                logging.debug('user_contest_id is {} of type {}'.format(user_contest_id, type(user_contest_id)))
                logging.debug('uc key is {} of type {}'.format(ucid, type(ucid)))
                logging.debug('user_contest_id equal to uc? {}'.format(int(ucid) == user_contest_id))

                ucid = int(ucid)
                if ucid == user_contest_id:
                    lineups[ucid]['my_lineup'] = True
                else:
                    lineups[ucid]['my_lineup'] = False

                lineups[ucid]['players'] = [{k: v for k, v in player.items() if k in wanted} for player in team]

            return lineups

        else:
            return None

    def hth_matchup(self, lineups):
        '''

        Args:
            lineups(dict):

        Returns:
            matchup(str):
        '''
        for lup in lineups.values():
            sal = 50000 - sum([p.get('s') for p in lup['players'] if isinstance(p.get('s'), (int, long))])
            pts = lup.get('pts')
            pmr = lup.get('pmr')
            l = [['{} {}'.format(p.get('fn'), p.get('ln')), p.get('pn'), p.get('s'), p.get('pts')] for p in lup['players']]
            if lup.get('my_lineup'):
                mine = l
                mine.append(['Points Scored', pts])
                mine.append(['Minutes Remaining', pmr])
                mine.append(['Salary Remaining', sal])
            else:
                opp = l
                opp.append(['Points Scored', pts])
                opp.append(['Minutes Remaining', pmr])
                opp.append(['Salary Remaining', sal])

        return tabulate.tabulate(list(zip(mine, opp)), headers = ['My Team', 'Opp Team'])

        #lines = ['MATCHUP REPORT']
        #lines.append(", ".join(['{} {}-{}'.format(p.get('fn'), p.get('ln'), p.get('pn')) for p in my_team.get('players')]))
        #lines.append(", ".join(['{} {}-{}'.format(p.get('fn'), p.get('ln'), p.get('pn')) for p in opp_team.get('players')]))
        #return '\n\n'.join(lines)

    def salaries(self):
        url = 'https://www.draftkings.com/lobby#/NFL/0/All'
        r = self.s.get(url)
        match = re.search(r'var packagedContests = (.*?);', r.content)
        if match:
            contest = json.loads(match.group(1))[0]
            dgid = contest.get('dg')
            curl = 'https://www.draftkings.com/lineup/getavailableplayerscsv?contestTypeId=21&draftGroupId={}'
            r = self.s.get(curl.format(dgid))
            f = StringIO.StringIO(r.content)
            dfr = pd.read_csv(f)
            return dfr.T.to_dict().values()
        else:
            return None


if __name__ == '__main__':
    pass
