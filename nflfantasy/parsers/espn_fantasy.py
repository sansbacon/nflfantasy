# -*- coding: utf-8 -*-

import logging
import re

from bs4 import BeautifulSoup
import unidecode

from nfl.dates import convert_format
from nfl.teams import nickname_to_code
from nfl.utility import merge_two


class ESPNFantasyParser(object):

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _fantasy_team_roster(self, t, team_id, league_name):
        '''
        Parses single table (one team) in fantasy_league_rosters
        Args:
            t: table element 

        Returns:
            list of dict
        '''
        players = []
        for tr in t.find_all('tr', {'id': re.compile(r'plyr')}):
            player = {'source_league_name': league_name}

            # source_team_name
            player['source_team_name'] = t.find('a', {'href': re.compile(r'ffl/clubhouse')}).text

            # loop through cells in row
            tds = tr.find_all('td')

            # slot
            player['roster_slot'] = tds[0].text

            # td[1]: name, team, pos
            ptp = tds[1].text
            if 'D/ST' in ptp:
                pattern = r'(.*?)\s+D/ST'
                match = re.match(pattern, ptp)
                if match:
                    player['source_player_name'] = '{} Defense'.format(match.group(1))
                    player['source_player_position'] = 'DST'
                    player['source_player_team'] = nickname_to_code(match.group(1))

            # [u'Kenny Stills', u'Mia WR  Q']
            # [u'Dexter McCluster', u'Ten RB']
            else:
                parts = [i for i in re.split(r',\s+', ptp, flags=re.DOTALL | re.MULTILINE) if i]
                if len(parts) == 2:
                    player['source_player_name'] = parts[0].strip().replace('*', ' ')
                    subparts = parts[1].split()
                    if len(subparts) >= 2:
                        player['source_player_team'], player['source_player_position'] = subparts[0:2]
                else:
                    raise ValueError('could not get player name')

            # a[0]: player_id
            a = tr.find('a', {'teamid': re.compile(r'\d+')})
            if a:
                player['source_player_id'] = a.attrs.get('playerid')
                player['source_league_id'] = a.attrs.get('leagueid')
                player['source_team_id'] = team_id
                player['season_year'] = int(a.attrs.get('seasonid'))

            # acquisition date & method
            method = tds[-1].text
            player['acquisition_method'] = method
            span = tds[-1].find('span')
            ad = span.attrs.get('title')
            if ad:
                player['acquisition_date'] = convert_format(ad, 'nfl')

            players.append(player)

        return players

    def drops(self, content):
        '''
        Parses recent drop/add page
        
        Args:
            content: 

        Returns:
            list of dict
        '''
        players = []
        soup = BeautifulSoup(content, 'lxml')
        colors = ['#f2f2e8', '#f8f8f2']
        for row in [tr for tr in soup.find_all('tr') if tr.attrs.get('bgcolor') in colors]:
            player = {'source': 'espn'}
            tds = row.find_all('td')
            player['transaction_date'] = tds[0].text
            player['transaction_type'] = tds[1].text.split()[-1]
            player['transaction_description'] = tds[2].text
            players.append(player)
        return players

    def fantasy_league_rosters(self, content):
        '''
        Parses page of entire league rosters
        
        Args:
            content: HTML string

        Returns:
            list of dict
        '''
        players = []
        soup = BeautifulSoup(content, 'lxml')

        # league name
        a = soup.find('a', {'href': re.compile(r'/ffl/leagueoffice\?leagueId')})
        if a:
            league_name = a.text
        else:
            league_name = 'Unknown'

        for idx, t in enumerate(soup.find_all('table', {'id': re.compile(r'playertable_')})):
            players += self._fantasy_team_roster(t, idx + 1, league_name)
        return players

    def fantasy_league_scoreboard(self, content):
        '''
        Gets league scoreboard from espn fantasy football
                
        Args:
            content: 

        Returns:
            list of dict: in_play, minutes_remaining, proj, team, team_record
        '''
        soup = BeautifulSoup(content, 'lxml')
        scores = []
        for tbl in soup.find_all('td', class_='matchupContainer'):
            score = {}
            for idx, tr in enumerate(tbl.find_all('tr')):
                # idx 0 is away team, 1 is home team, 2 is matchup information
                if idx == 0:
                    a = tr.find('a')
                    score['away_team'] = a.attrs.get('title')
                    for div in tr.find_all('div'):
                        for span in div.find_all('span'):
                            if span.attrs.get('title') == 'Record':
                                score['away_team_record'] = span.text.replace(')', '').replace('(', '')
                elif idx == 1:
                    a = tr.find('a')
                    score['home_team'] = a.attrs.get('title')
                    for div in tr.find_all('div'):
                        for span in div.find_all('span'):
                            if span.attrs.get('title') == 'Record':
                                score['home_team_record'] = span.text.replace(')', '').replace('(', '')
                elif idx == 2:
                    # first td is for the away team, second td is for home team
                    # have td for labels and td for players_played
                    # four tds in total away, away, home, home
                    # NOTE: something is not matching up, can't figure out 12/11
                    labels = [['away_yet_to_play', 'away_in_play', 'away_minutes_remaining', 'away_proj'],
                              ['home_yet_to_play', 'home_in_play', 'home_minutes_remaining', 'home_proj']]
                    players_played = [[item.text for item in pp.find_all('div')]
                                      for pp in tr.find_all('td', class_='playersPlayed')]
                    players_played = [[subitem.replace(u'\xa0', u' ') for subitem in item] for item in players_played]
                    for label, pp in zip(labels, players_played):
                        score = merge_two(score, dict(zip(label, pp)))

            scores.append(score)
        return scores

    def fantasy_team_roster(self, content):
        '''

        Args:
            content (str): HTML string from espn waiver wire page

        Returns:
            players (list): list of player dict
        '''
        players = []

        # remove * from player names
        soup = BeautifulSoup(content, 'lxml')
        for tr in soup.find_all('tr', {'id': re.compile(r'plyr')}):
            player = {'source': 'espn'}
            tds = tr.findAll('td')
            if not tds or len(tds) == 0:
                continue
            else:
                # td[0]: slot
                player['slot'] = tds[0].text

                # td[1]:
                ptp = tds[1].text
                if 'D/ST' in ptp:
                    pattern = r'(.*?)\s+D/ST'
                    match = re.match(pattern, ptp)
                    if match:
                        player['source_player_name'] = '{} Defense'.format(match.group(1))
                        player['source_player_position'] = 'DST'
                        player['source_player_team'] = nickname_to_code(match.group(1))
                        # a[0]: player_id
                        a = tr.find('a')
                        if a:
                            player['source_player_id'] = a.attrs.get('playerid')
                else:
                    a, navstr = list(tds[1].children)[0:2]
                    player['source_player_name'] = a.text
                    player['source_player_team'], player['source_player_position'] = navstr.split()[-2:]
                    player['source_player_id'] = a.attrs.get('playerid')

                # remove asterisk injury or news designation
                player['source_player_name'] = player.get('source_player_name', '').replace('*', ' ')
                players.append(player)

        return players

    def fantasy_waiver_wire(self, content):
        '''

        Args:
            content (str): HTML string from espn waiver wire page

        Returns:
            players (list): list of player dict
        '''
        players = []

        # irregular use of non-breaking spaces; easier to remove at start
        soup = BeautifulSoup(content, 'lxml')
        # league name
        a = soup.find('a', {'href': re.compile(r'/ffl/leagueoffice\?leagueId')})
        if a:
            league_name = a.text
        else:
            league_name = 'Unknown'

        t = soup.find('table', {'id': 'playertable_0'})

        #loop through rows in table
        for tr in t.findAll('tr', {'class': 'pncPlayerRow'}):
            player = {'source': 'espn', 'source_league_name': league_name}
            tds = tr.findAll('td')
            if not tds or len(tds) == 0:
                continue
            else:
                # td[0]: name, team, pos
                ptp = tds[0].text
                if 'D/ST' in ptp:
                    pattern = r'(.*?)\s+D/ST'
                    match = re.match(pattern, ptp)
                    if match:
                        player['source_player_name'] = '{} Defense'.format(match.group(1))
                        player['source_player_position'] = 'DST'
                        player['source_player_team'] = nickname_to_code(match.group(1))

                # [u'Kenny Stills', u'Mia WR  Q']
                # [u'Dexter McCluster', u'Ten RB']
                else:
                    parts = [i for i in re.split(r',\s+', tds[0].text, flags=re.DOTALL | re.MULTILINE) if i]
                    if len(parts) == 2:
                        player['source_player_name'] = parts[0].strip().replace('*', ' ')
                        subparts = parts[1].split()
                        if len(subparts) >= 2:
                            player['source_player_team'], player['source_player_position'] = subparts[0:2]
                    else:
                        logging.info(parts)

                # a[0]: player_id
                a = tr.find('a')
                if a:
                    player['source_player_id'] = a.attrs.get('playerid')

                # tds[2]: player status
                player['player_status'] = tds[2].text

                # tds[-2]: owernership
                player['player_own'] = tds[-2].text

                # tds[-1]: plus/minus
                player['player_own_pm'] = tds[-1].text.replace('+', '')

                players.append(player)

        return players

if __name__ == "__main__":
    pass
