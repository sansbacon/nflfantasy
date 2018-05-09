from __future__ import print_function

import json
import logging
import os
from pprint import pformat as pf
import re
import StringIO
import time

import pandas as pd

import browsercookie
import requests
import requests_cache
import tabulate


class DraftKingsNFLAgent(object):

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
    logging.basicConfig(level=logging.ERROR)
    a = DraftKingsNFLAgent()
    for contest in a.live_hth()[0:3]:
        print('CONTEST REPORT: {}'.format(contest['ContestId']))
        lineups = a.contest_lineups(contest['ContestId'], contest['UserContestId'], contest['DraftGroupId'])
        print(a.hth_matchup(lineups))
        print('\n\n')