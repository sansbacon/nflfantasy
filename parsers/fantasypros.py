# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, division

import logging
import json
import re

from bs4 import BeautifulSoup

from nfl.teams import long_to_code


class FantasyProsNFLParser(object):
    '''
    used to parse Fantasy Pros projections and ADP pages
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @property
    def formats(self):
        return ['std', 'ppr', 'hppr']

    @property
    def positions(self):
        return set(self.std_positions + self.ppr_positions)

    @property
    def ppr_positions(self):
        return ['rb', 'wr', 'te', 'flex', 'qb-flex']

    @property
    def std_positions(self):
        return ['qb', 'k', 'dst']

    def adp(self, content, season_year, scoring_format):
        '''
        Parses adp page
        
        Args:
            content (str): HTML
            season_year (int): 2018, etc.
            scoring_format (str): 'ppr', 'std', etc.

        Returns:
            list of player dict
            
        '''
        players = []
        soup = BeautifulSoup(content, 'lxml')
        for tr in soup.find('table', {'id': 'data'}).find('tbody').find_all('tr'):
            player = {'source': 'fantasypros',
                      'source_league_format': scoring_format,
                      'season_year': season_year}
            tds = tr.find_all('td')

            # exclude stray rows that don't have player data
            if len(tds) == 1:
                continue

            # try to find player id, name, and code
            try:
                acode, aid = [a for a in tr.find_all('a')
                              if 'tip' not in a.attrs['class']]
                player['source_player_code'] = acode['href'].split('/')[-1].split('.php')[0]
                player['source_player_name'] = acode.text
                player['source_player_id'] = int(aid.attrs.get('class')[-1].split('-')[-1])
            except:
                logging.exception('could not find playerid for {}'.format(player['source_player_name']))

            sm = tds[1].find_all('small')
            if sm and len(sm) == 2:
                player['source_team_code'] = sm[0].text
            elif sm:
                player['source_team_code'] = long_to_code(player['source_player_name'].split(' DST')[0].strip())
            else:
                player['source_team_code'] = 'UNK'

            # get remaining stats
            posrk = tds[2].text
            player['position_rank'] = int(''.join([s for s in posrk if s.isdigit()]))
            player['source_player_position'] = ''.join([s for s in posrk if not s.isdigit()])
            player['adp'] = float(tds[-1].text)

            # add to list
            players.append(player)

        return players

    def depth_charts(self, content, team, as_of=None):
        '''
        Team depth chart from fantasypros

        Args:
            content: HTML string
            team: string 'ARI', etc.
            as_of: datestr

        Returns:
            dc: list of dict
        '''
        dc = []
        soup = BeautifulSoup(content, 'lxml')
        for tr in soup.find_all('tr', {'class': re.compile(r'mpb')}):
            p = {'source': 'fantasypros', 'team_code': team, 'as_of': as_of}
            p['source_player_id'] = tr['class'][0].split('-')[-1]
            tds = tr.find_all('td')
            p['source_player_role'] = tds[0].text
            p['source_player_name'] = tds[1].text
            dc.append(p)
        return dc

    def draft_rankings_overall(self, content):
        '''
        Parses adp page

        Args:
            content: HTML string

        Returns:
            list of player dict
        '''
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', {'id': 'data'})
        headers = ['rank', 'player', 'pos', 'bye', 'best', 'worst', 'avg', 'stdev', 'adp', 'vs_adp']
        return [self._tr(tr, headers) for tr in t.find_all('tr', {'class': re.compile(r'mpb-player')})]

    def draft_rankings_position(self, content):
        '''
        Parses adp page
        
        Args:
            content: HTML string

        Returns:
            list of player dict
        '''
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', {'id': 'data'})
        headers = ['rank', 'player', 'bye', 'best', 'worst', 'avg', 'stdev', 'adp', 'vs_adp']
        return [self._tr(tr, headers) for tr in t.find_all('tr', {'class': re.compile(r'mpb-player')})]

    def projections(self, content, pos):
        '''
        Parses projections page

        Args:
            content: HTML string

        Returns:
            list of player dict
        '''
        pos = pos.upper()
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', {'id': 'data'})

        if pos == 'QB':
            headers = ['player', 'pass_att', 'pass_cmp', 'pass_yds', 'pass_td', 'pass_int',
                       'rush_att', 'rush_yds', 'rush_td', 'fl', 'fpts']
        elif pos == 'RB':
            headers = ['player', 'rush_att', 'rush_yds', 'rush_td', 'rcvg_rec', 'rcvg_yds', 'rcvg_tds', 'fl', 'fpts']
        elif pos == 'WR':
            headers = ['player', 'rush_att', 'rush_yds', 'rush_td', 'rcvg_rec', 'rcvg_yds', 'rcvg_tds', 'fl', 'fpts']
        elif pos == 'TE':
            headers = ['player', 'rcvg_rec', 'rcvg_yds', 'rcvg_tds', 'fl', 'fpts']
        elif pos == 'K':
            headers = ['player', 'fg', 'fga', 'xpt', 'fpts']
        elif pos == 'DST':
            headers = ['player', 'sack', 'int', 'fr', 'ff', 'td', 'assist', 'safety', 'pa', 'yds_agnst', 'fpts']

        return [self._tr(tr, headers) for tr in t.find_all('tr', {'class': re.compile(r'mpb-player')})]

    def _player_id_team(self, td):
        '''
        Handles player/id/team cell in fpros rankings
        
        Args:
            td: is a td element

        Returns:
            name, team, id
        '''
        id = None
        children = list(td.children)
        name = children[0].text
        team = children[2].text
        a = td.find('a', {'href': '#'})
        if a:
            try:
                id = a.attrs['data-fp-id']
            except:
                try:
                    id = a.attrs['class'][-1].split('-')[-1]
                except (KeyError, ValueError) as e:
                    logging.exception(e)
        return name, team, id

    def _week_pos(self, soup):
        '''
        Handles subtitle and position in fpros rankings

        Args:
            soup: parsed BeautifulSoup

        Returns:
            week, pos
        '''
        # <title>Week 1 QB Rankings, QB Cheat Sheets, QB Week 1 Fantasy Football Rankings</title>
        # but different locations on the half ppr and standard rankings pages
        positions = ['QB', 'WR', 'TE', 'DST', 'RB']
        title = soup.find('title')
        subtitle = title.text.split(', ')[0]
        week, pos = subtitle.split()[1:3]
        if not week.isdigit:
            for span in soup.find_all('span'):
                if 'Week' in span.text:
                    week = span.text.split()[-1]
                else:
                    week = None
        if not pos in positions:
            for li in soup.find_all('li', {'class': 'active'}):
                a = li.find('a')
                if a:
                    pos = a.text
                else:
                    pos = None
        return week, pos

    def flex_weekly_rankings(self, content, fmt, season_year, week):
        results = []
        soup = BeautifulSoup(content, 'lxml')
        for tr in soup.find_all('tr', {'class': re.compile(r'mpb-player')}):
            player = {'source': 'fantasypros', 'season_year': season_year, 'week': week,
                      'scoring_format': fmt, 'ranking_type': 'flex'}

            tds = tr.find_all('td')

            # tds[0]: rank
            player['rank'] = tds[0].text

            # tds[2]: player/id/team
            player['source_player_name'], player['source_player_team'], player['source_player_id'] = \
                self._player_id_team(tds[2])

            # tds[3]: posrank
            try:
                player['source_player_posrk'] = int(''.join([i for i in tds[3].text if i.isdigit()]))
                player['source_player_position'] = ''.join([i for i in tds[3].text if not i.isdigit()])
            except:
                pass

            # tds[4]: opp
            try:
                player['source_player_opp'] = tds[4].text.split()[-1]
            except:
                pass

            # tds[5:9] data
            for k,v in zip(['best', 'worst', 'avg', 'stdev'], [td.text for td in tds[5:9]]):
                player[k] = v

            # get last updated
            try:
                player['source_last_updated'] = soup.select('h5 time')[0].attrs.get('datetime').split()[0]
            except:
                pass

            results.append(player)
        return results

    def expert_rankings(self, content):
        '''
        FantasyPros responds with javascript function 
        This python function turns that response into a dict    

        Args:
            content (str): text property of response

        Returns:
            list: list of dict

        '''
        results = []
        patt = re.compile(r'FPWSIS.compareCallback\((.*?)\);')
        match = re.search(patt, content)
        if match:
            rankings = json.loads(match.group(1)).get('rankings')
            for fmt in ['PPR', 'HALF', 'STD']:
                if rankings.get(fmt):
                    ranks = rankings[fmt]
                    for pid, pidranks in ranks.items():
                        try:
                            results.append({'player_id': pid,
                                            'expert_rank': pidranks[0]['rank'],
                                            'scoring_fmt': fmt.lower(),
                                            'expert_id': pidranks[0]['expert_id'],
                                            'consensus_rank': pidranks[1]['rank']})
                        except:
                            logging.exception('could not add {}'.format(pidranks))
        else:
            logging.error('could not parse response into JSON: {}'.format(content))

        return results

    def weekly_rankings(self, content, fmt, pos, season_year, week):
        '''
        Parses weekly rankings page for specific position

        Args:
            content: HTML string

        Returns:
            list of player dict
        '''
        # table structure is different for flex rankings, so use separate function
        if pos.lower() == 'flex':
            return self.flex_weekly_rankings(content=content, fmt=fmt, season_year=season_year, week=week)

        results = []
        soup = BeautifulSoup(content, 'lxml')
        for tr in soup.find_all('tr', {'class': re.compile(r'mpb-player')}):
            player = {'source': 'fantasypros', 'season_year': season_year, 'week': week,
                      'scoring_format': fmt, 'ranking_type': 'pos', 'source_player_position': pos.upper()}
            tds = tr.find_all('td')

            # tds[0]: rank
            player['rank'] = tds[0].text

            # tds[2]: player/id/team
            player['source_player_name'], player['source_player_team'], player['source_player_id'] = \
                self._player_id_team(tds[2])

            # tds[3]: opp
            try:
                player['source_player_opp'] = tds[3].text.split()[-1]
            except:
                pass

            # tds[4:8] data
            for k,v in zip(['best', 'worst', 'avg', 'stdev'], [td.text for td in tds[4:8]]):
                player[k] = v

            # get last updated
            try:
                player['source_last_updated'] = soup.select('h5 time')[0].attrs.get('datetime').split()[0]
            except:
                pass

            results.append(player)
        return results

    def player_weekly_rankings(self, content):
        '''
        Parses weekly rankings page for specific player

        Args:
            content (str): HTML 

        Returns:
            list of dict
            
        '''
        results = []
        soup = BeautifulSoup(content, 'lxml')
        tbl = soup.select('table.expert-ranks')[0]

        # get season
        season = None
        for th in [h.text for h in tbl.find_all('th')]:
            if 'Accuracy' in th:
                season = re.sub('[^0-9]', '', th)
                break

        # get week
        week = re.sub('[^0-9]','', soup.select('div.subhead.pull-left')[0].text)

        # get player slug
        a = soup.find('a', {'href': re.compile('/nfl/projections/\w+-+\w+.php')})
        slug = a['href'].split('.php')[0].split('/')[-1]

        # get player id and name
        h1 = soup.find('h1')
        source_player_name = h1.text
        source_player_id = h1['class'][0].split('-')[-1]

        # get player position and team
        h5 = soup.find('h5')
        source_player_position, source_player_team = [val.strip() for val in h5.text.split('-')]

        # get format
        fmt_d = {'Standard': 'std', 'PPR': 'ppr', 'Half PPR': 'hppr'}
        for div in soup.find_all('div', class_='pull-right'):
            if 'Half PPR' in div.text:
                for option in div.find_all('option'):
                    if option.get('selected') == "" and option.text in fmt_d:
                        fmt = fmt_d.get(option.string)

        # now loop through rankings
        for tr in tbl.find('tbody').find_all('tr'):
            # figure out everything we want here
            rank = {'source': 'fantasypros', 'season_year': season, 'week': week,
                    'scoring_format': fmt, 'ranking_type': 'weekly', 'source_player_id': source_player_id,
                    'source_player_name': source_player_name, 'source_player_team': source_player_team,
                    'source_player_position': source_player_position, 'source_player_code': slug}

            tds = tr.find_all('td')
            # tds[0]: expert name
            rank['expert_name'] = tds[0].text
            # tds[1]: affiliation
            rank['expert_affiliation'] = tds[1].text
            # tds[2]: rank
            # strip non-numeric characters
            rank['source_positional_rank'] = re.sub('[^0-9]','', tds[2].text)
            # tds[3]: rank_vs_ecr
            rank['source_positional_rank_vs_ecr'] = tds[3].text
            # all set
            results.append(rank)
        return results

    def player_weekly_results(self, content, pos):
        '''
        Parses weekly rankings page for specific player

        Args:
            content (str): HTML 
            pos (str): qb, rb, etc.
            
        Returns:
            list of dict

        '''
        results = []
        soup = BeautifulSoup(content, 'lxml')

        # get season
        try:
            season = int(re.search(r'\d+', soup.find('h1').text).group())
        except:
            season = None

        # get week
        try:
            week = int(re.search(r'\d+', soup.find('h5').text).group())
        except:
            week = None

        tbl = soup.select('table#data')[0]
        for tr in tbl.tbody.find_all('tr'):
            if pos == 'dst':
                # get player slug and name
                a = tr.find('a', {'href': re.compile('/nfl/.*?/(.*?).php')})
                slug = a['href'].split('.php')[0].split('/')[-1]
                source_player_name = a.text
                tds = tr.find_all('td')
                fpts = float(tds[2].text)
                results.append((season, week, slug, source_player_name, fpts))

        return results


if __name__ == "__main__":
    pass