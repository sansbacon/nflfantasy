# -*- coding: utf-8 -*-
# nflfantasy/draft.py
# scraper/parser for DRAFT.com

import json
import logging
from operator import itemgetter
import re

from nflmisc.scraper import FootballScraper
from nfl.utility import merge_two


class Scraper(FootballScraper):
    '''

    '''
    def _json_file(self, fn):
        '''
        Opens JSON file from disk

        Args:
            fn:

        Returns:
            dict: JSON parsed into dict

        '''
        with open(fn, 'r') as infile:
            return json.load(infile)

    def adp(self, start_date, end_date, season_year, participants, entry_cost, token):
        '''

        Args:
            start_date:
            end_date:
            season_year:
            participants:
            entry_cost:
            token:

        Returns:
            dict

        '''
        url = 'https://api.playdraft.com/feeds/v2/sports/nfl//season/adp?'
        params = {'start_date': start_date,
                  'end_date': end_date,
                  'year': season_year,
                  'participants': participants,
                  'entry_cost': entry_cost,
                  'token': token}
        return self.get_json(url, params)

    def complete_contests(self, fn=None):
        '''

        Args:
            fn (str):

        Returns:
            dict

        '''
        if fn:
            return self._json_file(fn)
        else:
            url = 'https://api.playdraft.com/v1/window_clusters/2015/complete_contests'
            return self.get_json(url=url)

    def draft(self, league_id=None, fn=None):
        '''

        Args:
            league_id (str):
            fn (str):

        Returns:
            dict

        '''
        if fn:
            return self._json_file(fn)
        elif league_id:
            url = 'https://api.playdraft.com/v3/drafts/{}'
            return self.get_json(url=url.format(league_id))
        else:
            return ValueError('must specify league_id or fn')

    def player_pool(self, pool_id=None, fn=None):
        '''

        Args:
            fn (dict):

        Returns:
            dict

        '''
        if fn:
            return self._json_file(fn)
        elif pool_id:
            url = 'https://api.playdraft.com/v4/player_pool/{}'
            return self.get_json(url.format(pool_id))
        else:
            return ValueError('must specify pool_id or fn')


class Parser():
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _combine_bookings_players(self, bookings, players):
        '''
        Combines players and bookings

        Args:
            bookings (list): of dict
            players (list): of dict

        Returns:
            list: of dict

        '''
        merged = []

        # go through bookings first
        # create bookings dict with player_id: player_dict
        b_wanted = ['id', 'player_id', 'booking_id', 'adp', 'position_id', 'projected_points']
        bookingsd = {}
        for b in bookings:
            pid = b['player_id']
            bd = {k: v for k, v in b.items() if k in b_wanted}
            bd['booking_id'] = bd.pop('id')
            bookingsd[pid] = bd

        # now try to match up with players
        p_wanted = ['first_name', 'last_name', 'team_id', 'injury_status']
        for p in players:
            match = bookingsd.get(p['id'])
            if match:
                merged.append(merge_two(match, {k: v for k, v in p.items()
                                                if k in p_wanted}))
        return merged

    def _teams(self, teams):
        '''
        Creates list teams and teamsd (id: team)

        Args:
            teams (list):

        Returns:
            tuple

        '''
        twanted = ['abbr', 'city', 'id', 'nickname']
        self.teams = [{k: v for k, v in t.items() if k in twanted} for t in teams]
        self.teamsd = {t['id']: t['abbr'] for t in self.teams}
        return (self.teams, self.teamsd)

    def adp(self, content):
        '''

        Args:
            content:

        Returns:
            list: of dict (name, team, adp, sportradar_id, min_pick, max_pick, position)

        '''
        return content['average_draft_positions']

    def complete_contests(self, cc, season_year):
        '''
        Parses complete_contests resource. Does not get list of draft picks.

        Args:
            cc (dict): complete contests json file
            season_year (int): 2018, etc.

        Returns:
            list: of contest dict

        '''
        return [{'prize': float(dr['prize']), 'player_pool_id': dr['time_window_id'],
                 'entry_cost': float(dr['entry_cost']),
                 'draft_time': dr['draft_time'],
                 'participants': dr['max_participants'],
                 'league_id': dr['id'], 'season_year': season_year,
                 'league_json': dr} for dr in cc['drafts']]

    def draft_users(self, draft):
        '''
        Parses single draft resource into users and user_league

        Args:
            draft (dict):

        Returns:
            tuple: (list of dict, list of dict)

        '''
        if draft.get('draft'):
            draft = draft['draft']
        uwanted = ['experienced', 'id', 'skill_level', 'username']
        users = [{k: v for k, v in user.items() if k in uwanted}
                 for user in draft['users']]
        league_users = [{'league_id': draft['id'],
                         'user_id': dr['user_id'],
                         'pick_order': dr['pick_order']}
                        for dr in draft['draft_rosters']]
        return users, league_users

    def draft_picks(self, draft):
        '''
        Parses single draft resource into picks

        Args:
            draft (dict):

        Returns:
            list: of dict

        '''
        picks = []
        if draft.get('draft'):
            draft = draft['draft']
        teams, teamsd = self._teams(draft['teams'])
        posd = {int(pos['id']): pos['name'] for pos in draft['positions']}

        # players
        players = []
        for p in self._combine_bookings_players(draft['bookings'], draft['players']):
            tid = p.get('team_id')
            if tid:
                p['team_abbr'] = teamsd.get(tid, 'FA')
            else:
                p['team_abbr'] = 'FA'

            p['position'] = posd.get(p['position_id'])
            players.append(p)

        # bookings_xref
        player_bookings_d = {p['booking_id']: p for p in players}

        # picks
        rosters = draft['draft_rosters']
        pkwanted = ['booking_id', 'id', 'draft_roster_id', 'pick_number', 'slot_id']
        for t in rosters:
            for pick in [{k: v for k, v in pk.items() if k in pkwanted} for pk in t['picks']]:
                pick['user_id'] = t['user_id']
                pick['league_id'] = draft['id']

                # add player data
                match = player_bookings_d.get(pick['booking_id'])
                if match:
                    pickc = merge_two(pick, match)
                else:
                    logging.info('no bookings match for {}'.format(pickc))
                picks.append(pickc)
        return picks

    def player_pool(self, pp, pool_date):
        '''
        Parses player_pool resource

        Args:
            pp (dict): player_pool resource - parsed JSON into dict
            pool_date (str): e.g. '2018-04-10'

        Returns:
            list: of dict

        '''
        # no need for top-level 'player_pool' key
        if pp.get('player_pool'):
            pp = pp['player_pool']

        # unique identifier for player pool
        # changes over time (example - no Nick Chubb)
        player_pool_id = pp['id']

        teams, teamsd = self._teams(pp['teams'])
        posd = {int(pos['id']): pos['name'] for pos in pp['positions']}

        # loop through booking + player and add fields
        players = []
        ppwanted = ['adp', 'first_name', 'last_name', 'player_id', 'pool_date', 'booking_id',
                    'season_year', 'player_pool_id', 'position', 'team', 'projected_points']
        for pl in self._combine_bookings_players(pp['bookings'], pp['players']):
            pl['player_pool_id'] = player_pool_id
            pl['position'] = posd.get(pl['position_id'])
            pl['team'] = teamsd.get(pl['team_id'], 'FA')
            pl['pool_date'] = pool_date
            pl['season_year'] = int(pool_date[0:4])
            players.append({k: v for k, v in pl.items() if k in ppwanted})
        return players


class CSVParser(object):
    '''
    Parses data dump from DRAFT about past season
    '''

    def team_total(self, team):
        '''
        Calculate season score for bestball team

        Args:
            team (list): of player dict

        Returns:
            float: team score for season

        '''
        tot = 0
        for week in range(1, 17):
            ids = []
            week_key = 'w{}'.format(week)
            qbs = sorted([p for p in team if p['position'] == 'QB'],
                         key=itemgetter(week_key), reverse=True)
            rbs = sorted([p for p in team if p['position'] == 'RB'],
                         key=itemgetter(week_key), reverse=True)
            wrs = sorted([p for p in team if p['position'] == 'WR'],
                         key=itemgetter(week_key), reverse=True)
            tes = sorted([p for p in team if p['position'] == 'TE'],
                         key=itemgetter(week_key), reverse=True)

            if len(qbs) > 0:
                ids.append(qbs[0]['player_id'])
            logging.debug('ids is now {}'.format(len(ids)))
            if len(rbs) >= 2:
                ids += [p['player_id'] for p in rbs[0:2]]
            elif len(rbs) == 1:
                ids.append(rbs[0]['player_id'])
            logging.debug('ids is now {}'.format(len(ids)))

            if len(wrs) >= 3:
                ids += [p['player_id'] for p in wrs[0:3]]
            elif len(wrs) == 2:
                ids += [p['player_id'] for p in wrs[0:2]]
            elif len(wrs) == 1:
                ids.append(wrs[0]['player_id'])
            logging.debug('ids is now {}'.format(len(ids)))

            if len(tes) > 0:
                ids.append(tes[0]['player_id'])

            logging.debug('ids is now {}'.format(len(ids)))

            # now address the flex
            for p in sorted(rbs + wrs + tes,
                            key=itemgetter(week_key), reverse=True):
                if p['player_id'] not in ids:
                    ids.append(p['player_id'])
                    break

            logging.debug('ids is now {}'.format(len(ids)))

            scores = [p[week_key] for p in team if p['player_id'] in ids]
            week_tot = sum(scores)
            logging.debug('{} is {}'.format(week_key, week_tot))
            tot += week_tot

        return tot


class Agent(object):
    '''
    '''

    adp_headers = {
                      'X-Client-Sha': 'fd31c977023d4fb3ff7b98e0d20e7861ad2ecea0',
                      'Origin': 'https://draft.com',
                      'Accept-Encoding': 'gzip, deflate, br',
                      'X-User-Token': 'AXEcExsKNHPwxQZBbZCM',
                      'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
                      'X-User-Auth-Id': 'afcd9e4f-5b7d-4e21-96ae-3801cc24f968',
                      'Connection': 'keep-alive',
                      'Pragma': 'no-cache',
                      'X-Build-Number': '0',
                      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                    'Chrome/65.0.3325.181 Safari/537.36',
                      'Accept': 'application/json, text/javascript, */*; q=0.01',
                      'Cache-Control': 'no-cache',
                      'Referer': 'https://draft.com/rankings/11416',
                      'X-Client-Type': 'web',
                      'DNT': '1',
                  },

    cc_headers = {
        'X-Client-Sha': 'fd31c977023d4fb3ff7b98e0d20e7861ad2ecea0',
        'Origin': 'https://draft.com',
        'X-Client-Type': 'web',
        'X-Build-Number': '0',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 '
                      'Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-User-Token': 'AXEcExsKNHPwxQZBbZCM',
        'X-User-Auth-Id': 'afcd9e4f-5b7d-4e21-96ae-3801cc24f968',
        'Referer': 'https://draft.com/upcoming',
        'Connection': 'keep-alive',
        'DNT': '1',
    }

    draft_headers = {
        'X-Client-Sha': 'fd31c977023d4fb3ff7b98e0d20e7861ad2ecea0',
        'Origin': 'https://draft.com',
        'X-Client-Type': 'web',
        'X-Build-Number': '0',
        'Accept-Encoding': 'gzip, deflate, br',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 '
                      'Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-User-Token': 'AXEcExsKNHPwxQZBbZCM',
        'X-User-Auth-Id': 'afcd9e4f-5b7d-4e21-96ae-3801cc24f968',
        'Referer': 'https://draft.com/upcoming?draft_id=8d5f5c8d-5971-48bd-b4ff-0491278d689c&draft_type=draft',
        'Connection': 'keep-alive',
        'DNT': '1',
    }

    def __init__(self, cc_headers, draft_headers, cache_name='draft-nfl-agent'):
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()
        self.cc_headers = cc_headers
        self.draft_headers = draft_headers

    def complete_contests(self, cc_headers):
        '''
        Gets complete_contests resource, saves to db

        Args:
            cc_headers (dict):

        Returns:
            list: of dict

        '''
        pass

    def draft(self, headers):
        '''
        Gets complete_contests resource, saves to db

        Args:
            headers (dict):

        Returns:
            list: of dict

        '''
        pass


if __name__ == '__main__':
    pass
