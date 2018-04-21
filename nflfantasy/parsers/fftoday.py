# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging
import re

from bs4 import BeautifulSoup

from NFLProjectionsParser import NFLProjectionsParser


class FFTodayParser(NFLProjectionsParser):
    '''
    Parses html of NFL fantasy projections page of fantasyfootballtoday.com into player dictionaries

    Example:
        p = FFTodayParser()
        players = p.projections(content)
    '''

    def __init__(self):
        '''
        '''


    def _parse_dst_row(self, row):

        player = {}

        # headers goofy to parse, so hardcode them here, plus don't need all data
        # headers = ['player_id', 'full_name', 'team', 'bye', 'fpts']

        # get the player name / id that is in the url of the 'a' element
        link = row.find('a')

        if link:
            url_pattern = re.compile(r'/stats/players\?TeamID\=(\d+)')
            m = re.search(url_pattern, link.get('href'))
        else:
            logging.debug('could not find link in %s' % row.prettify())

        if m:
            player['fftoday_id'] = m.group(1)
            player['full_name'] = self._fix_team_code(link.string)

        # I want the 3rd and last <td class=sort1 align=center>
        tds = row.findAll('td', {'class': 'sort1', 'align': 'center'})

        bye_td = tds[1]
        player['bye'] = bye_td.string

        fpts_td = tds[-1]
        player['fantasy_points'] = fpts_td.string

        return player

    def _parse_row(self, row):
        player = {}  
    
        # headers goofy to parse, so hardcode them here, plus don't need all data
        # headers = ['player_id', 'full_name', 'team', 'bye', 'fpts']
                
        # get the player name / id that is in the url of the 'a' element
        link = row.find('a')

        if link:
            url_pattern = re.compile(r'/stats/players/(.*?)/(.*?)\?')
            m = re.search(url_pattern, link.get('href'))
        else:
            logging.debug('could not find link in %s' % row.prettify())

        if m:
            player['fftoday_id'] = m.group(1)
            player['full_name'] = m.group(2).replace("_", " ")

        # I want the 2nd, 3rd, and last <td class=sort1 align=center>
        tds = row.findAll('td', {'class': 'sort1', 'align': 'center'})       

        team_td = tds[1]
        player['team'] = team_td.string

        bye_td = tds[2]
        player['bye'] = bye_td.string

        fpts_td = tds[-1]
        player['fantasy_points'] = fpts_td.string

        return player

    def _parse_page(self, content, position):
        players = []
        soup = BeautifulSoup(content)

        table = soup.find('table', {'cellpadding': '2', 'border': '0', 'cellspacing': '1'})

        if position == 'dst':
            for tr in table.findAll('tr', attrs={'class': None}):
                player = self._parse_dst_row(tr)
                player['position'] = 'dst'
                players.append(player)

        else:
            for tr in table.findAll('tr', attrs={'class': None}):
                player = self._parse_row(tr)
                player['position'] = position
                players.append(player)
        
        return players

    def _pid(self,href):
        '''
        Different format for DST vs. other URLs
        '''
        if 'TeamID' in href:
            '''
            Mysterious failure of regex here - works in online regex tester
            #< A HREF = "/stats/players?TeamID=9016&amp;LeagueID=168784" > Philadelphia Eagles < / A > < / TD >
            #pattern = re.compile('(\d+)&', re.UNICODE)
            #match = re.match(pattern, href)
            # if match:
            #    pid = match.group(1)
            '''

            tid = href.split('?')[1]
            tid = tid.split('=')[1]
            tid = tid.split('&')[0]

            if tid:
                pid = tid
            else:
                pid = href

        else:
            pattern = re.compile('/stats/players/(\d+)', re.UNICODE)
            match = re.match(pattern, href)
            if match:
                pid = match.group(1)
            else:
                pid = href

        return pid

    def _teams(self, name):

        names = {'Arizona': 'ARI', 'Atlanta': 'ATL', 'Baltimore': 'BAL', 'Buffalo': 'BUF', 'Carolina': 'CAR',
                 'Chicago': 'CHI', 'Cincinnati': 'CIN', 'Cleveland': 'CLE', 'Dallas': 'DAL', 'Denver': 'DEN',
                 'Detroit': 'DET', 'Green Bay': 'GB', 'Houston': 'HOU', 'Indianapolis': 'IND', 'Jacksonville': 'JAC',
                 'Kansas City': 'KC', 'Miami': 'MIA', 'Minnesota': 'MIN', 'New England': 'NE', 'New Orleans': 'NO',
                 'NY Giants': 'NYG', 'NY Jets': 'NYJ', 'Oakland': 'OAK', 'Philadelphia': 'PHI', 'Pittsburgh': 'PIT',
                 'San Diego': 'SD', 'San Francisco': 'SF', 'Seattle': 'SEA', 'St. Louis': 'STL', 'Tampa Bay': 'TB',
                 'Tennessee': 'TEN', 'Washington': 'WAS', 'JACK': 'JAC', 'WSH': 'WAS', 'Cardinals': 'ARI',
                 'Falcons': 'ATL', 'Ravens': 'BAL', 'Bills': 'BUF', 'Panthers': 'CAR', 'Bears': 'CHI', 'Bengals': 'CIN',
                 'Browns': 'CLE', 'Cowboys': 'DAL', 'Broncos': 'DEN', 'Lions': 'DET', 'Packers': 'GB', 'Texans': 'HOU',
                 'Colts': 'IND', 'Jaguars': 'JAC', 'Chiefs': 'KC', 'Dolphins': 'MIA', 'Vikings': 'MIN',
                 'Patriots': 'NE', 'Saints': 'NO', 'Giants': 'NYG', 'Jets': 'NYJ', 'Raiders': 'OAK', 'Eagles': 'PHI',
                 'Steelers': 'PIT', 'Chargers': 'SD', '49ers': 'SF', 'Seahawks': 'SEA', 'Rams': 'LARM',
                 'Buccaneers': 'TB', 'Titans': 'TEN', 'Redskins': 'WAS', 'Buffalo Bills': 'BUF',
                 'Seattle Seahawks': 'SEA', 'Philadelphia Eagles': 'PHI', 'St. Louis Rams': 'LARM', 'Los Angeles Rams': 'LARM',
                 'Arizona Cardinals': 'ARI', 'Carolina Panthers': 'CAR', 'Green Bay Packers': 'GB',
                 'New England Patriots': 'NE', 'Dallas Cowboys': 'DAL', 'Detroit Lions': 'DET',
                 'Kansas City Chiefs': 'KAN', 'Houston Texans': 'HOU', 'Baltimore Ravens': 'BAL',
                 'New York Giants': 'NYG', 'Denver Broncos': 'DEN', 'Chicago Bears': 'CHI', 'Miami Dolphins': 'MIA',
                 'San Francisco 49ers': 'SAN', 'Cincinnati Bengals': 'CIN', 'Cleveland Browns': 'CLE',
                 'Indianapolis Colts': 'IND', 'Minnesota Vikings': 'MIN', 'Washington Redskins': 'WAS',
                 'Jacksonville Jaguars': 'JAC', 'Pittsburgh Steelers': 'PIT', 'Atlanta Falcons': 'ATL',
                 'New Orleans Saints': 'NO', 'Tennessee Titans': 'TEN', 'Tampa Bay Buccaneers': 'TB',
                 'New York Jets': 'NYJ', 'Oakland Raiders': 'OAK', 'San Diego Chargers': 'SD'
                 }
        return names.get(name)

    def _wrn(self, td):
        
        pattern = r'(\d+)\.+\s+(\w+.*)'           
        match = re.match(pattern, td)

        if match:                                 
            return match.group(1), match.group(2)        
        else:
            return None


    def fix_header(self, header):
        '''
        Looks at global list of headers, can provide extras locally
        :param headers:
        :return:
        '''

        fixed = {
        }

        # return fixed.get(header, header)
        fixed_header = self._fix_header(header)
        logging.debug('parser._fix_header fixed header')
        logging.debug(fixed_header)

        # fixed_header none if not found, so use local list
        if not fixed_header:
            return fixed.get(header, header)

        else:
            return fixed_header


    def fix_headers(self, headers):
        '''

        :param headers:
        :return:
        '''
        return [self.fix_header(header) for header in headers]


    def projections (self, content):
        '''
        Parses all pages, which have rows of html table using BeautifulSoup and returns list of player dictionaries
        Args:
            content (dictionary): keys are positions, values are list of html pages
        Returns:
            List of dictionaries if successful, empty list otherwise.
        '''
        players = []
        for position, pages in content.items():
            for page in pages:
                parsed = self._parse_page(page, position)           
                if parsed:
                    players = players + parsed

        return players

    def _parse(self, content, headers, season, week, pos):
        players = []

        soup = BeautifulSoup(content, 'lxml')
        table = soup.find('table', {'cellpadding': 2, 'cellspacing': 1, 'border': 0})

        for tr in table.findAll('tr')[2:]:
            td = tr.find('td')
            if td:
                a = td.find('a')
                if a:
                    tds = [td.text.strip() for td in tr.findAll('td')]
                    player = dict(zip(headers, tds[1:]))
                    player['season'] = season
                    player['week'] = week
                    player['pos'] = pos
                    player['site_player_id'] = _pid(a['href'])
                    rankname = tds[0]
                    if rankname:
                        try:
                            player['weekly_rank'], player['site_player_name'] = _wrn(rankname)
                        except:
                            logging.error('_parse: could not parse rankname')

                    # fix for DST
                    if pos == 'DST':
                        player['team'] = _teams(player['site_player_name'])
                        player['site_player_name'] = player['site_player_name'].split(' ')[-1] + ' DST'

                    # prepare for database
                    player['site'] = 'fftoday'
                    player.pop('g')
                    player.pop('weekly_rank')
                    player.pop('fantasy_points_g')

                    players.append(player)

                else:
                    logging.error('_parse: could not find <a> element')
            else:
                logging.error('_parse: could not find <td> element')

        return players

    def weekly_results(self, content, season, week, position):
        '''
        Need a different parser for each position type
        '''
        if position == 'DST':
            headers = ['g', 'sack', 'fumbles_recovered', 'interceptions', 'def_td', 'points_allowed', 'pass_yds_allowed', 'rush_yds_allowed', 'safety', 'kick_td', 'fantasy_points', 'fantasy_points_g']
            return self._parse(content, headers, season, week, 'DST')

        elif position == 'QB':
            headers = ['team', 'g', 'pass_cmp', 'pass_att', 'pass_yds', 'pass_td', 'pass_int', 'rush_att', 'rush_yds', 'rush_td', 'fantasy_points', 'fantasy_points_g']
            return self._parse(content, headers, season, week, 'QB')

        elif position == 'RB':
            headers = ['team', 'g', 'rush_att', 'rush_yds', 'rush_td', 'rec_target', 'rec_rec', 'rec_yds', 'rec_td', 'fantasy_points', 'fantasy_points_g']
            return self._parse(content, headers, season, week, 'RB')

        elif position == 'TE':
            headers = ['team', 'g', 'rec_target', 'rec_rec', 'rec_yds', 'rec_td', 'fantasy_points', 'fantasy_points_g']
            return self._parse(content, headers, season, week, 'TE')

        elif position == 'WR':
            headers = ['team', 'g', 'rec_target', 'rec_rec', 'rec_yds', 'rec_td', 'rush_att', 'rush_yds', 'rush_td', 'fantasy_points', 'fantasy_points_g']
            return self._parse(content, headers, season, week, 'WR')

        else:
            return None


    def weekly_rankings(self, content):
        """
        Parses weekly rankings page
        
        Args:
            content: 

        Returns:
            list of dict
        """
        soup = BeautifulSoup(content, 'lxml')
        for t in soup.find_all('table', {'width': '100%', 'border': '0', 'cellpadding': '0', 'cellspacing': '0'}):
            pass # do something here


if __name__ == '__main__':
    pass
