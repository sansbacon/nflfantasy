'''

# nflfantasy/fantasypros.py
# scraper/parser/agent for fantasypros.com

'''

import itertools
import logging
import re
import time

import pandas as pd
from bs4 import BeautifulSoup

from sportscraper.scraper import RequestScraper, WaybackScraper
from nfl.seasons import get_season
from nfl.teams import long_to_code


class Scraper(RequestScraper):
    '''

    '''

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

    def _construct_url(self, pos, fmt, cat):
        '''
        Creates url for rankings or projections pages

        Args:
            pos(str): 'qb', etc.
            fmt(str): 'ppr', 'std', 'hppr'
            cat(str): rankings or projections

        Returns:
            url string
        '''
        if fmt not in self.formats:
            raise ValueError('invalid format: {}'.format(fmt))

        if pos not in self.positions:
            raise ValueError('invalid format: {}'.format(fmt))

        url = f'https://www.fantasypros.com/nfl/{cat}/{pos}.php'
        if pos in self.ppr_positions:
            if fmt == 'std':
                url = f'https://www.fantasypros.com/nfl/{cat}/{pos}.php'
            elif fmt == 'ppr':
                url = f'https://www.fantasypros.com/nfl/{cat}/ppr-{pos}.php'
            elif fmt == 'hppr':
                url = f'https://www.fantasypros.com/nfl/{cat}/half-point-ppr-{pos}.php'
        return url

    def adp(self, fmt):
        '''
        Gets ADP page

        Args:
            fmt(str): 'std', 'ppr'

        Returns:
            content: HTML string of page
        '''
        if fmt == 'std':
            url = 'https://www.fantasypros.com/nfl/adp/overall.php'
        elif fmt == 'ppr':
            url = 'https://www.fantasypros.com/nfl/adp/ppr-overall.php'
        else:
            raise ValueError('invalid format: %s', fmt)
        return self.get(url)

    def draft_rankings(self, pos, fmt):
        '''
        Gets draft rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'rankings')
        return self.get(url)

    def player_weekly_rankings(self, pid, fmt, week):
        '''

        Args:
            pid:
            fmt:
            week:

        Returns:

        '''
        # https://www.fantasypros.com/nfl/rankings/tom-brady.php?type=weekly&week=2&scoring=PPR
        url = f'https://www.fantasypros.com/nfl/rankings/{pid}.php?'
        params = {'type': 'weekly',
                  'week': week,
                  'scoring': fmt
                  }
        return self.get(url, params=params)

    def projections(self, pos, fmt, week):
        '''
        Gets rest-of-season rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'
            week: 'draft' or 1-17

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'projections')
        params = {'week': week}
        return self.get(url, params=params)

    def ros_rankings(self, pos, fmt):
        '''
        Gets rest-of-season rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'rankings')
        url = url.replace('rankings/', 'rankings/ros-')
        return self.get(url)

    def weekly_rankings(self, pos, fmt, week=None):
        '''
        Gets weekly rankings page

        Args:
            pos: 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt: 'std', 'ppr', 'hppr'
            week: default None, int between 1-17

        Returns:
            content: HTML string of page
        '''
        url = self._construct_url(pos, fmt, 'rankings')
        params = {}
        if week:
            params = {'week': week}
        return self.get(url, params=params)

    def weekly_scoring(self, pos, params, fmt=None):
        '''

        Args:
            pos (str): qb, rb, etc.

        Returns:

        '''
        if fmt:
            url = f'https://www.fantasypros.com/nfl/reports/leaders/{fmt}-{pos.lower()}.php?'
        else:
            url = f'https://www.fantasypros.com/nfl/reports/leaders/{pos.lower()}.php?'
        return self.get(url, params=params)


class WScraper(WaybackScraper):
    '''
    '''

    def weekly_rankings(self, pos, fmt, datestr):
        '''
        Gets weekly rankings page

        Args:
            pos(str): 'qb', 'rb', 'wr', 'te', 'flex', 'qb-flex', 'k', 'dst'
            fmt(str): 'std', 'ppr', 'hppr'
            datestr(str): datestring for closest week in wayback

        Returns:
            tuple: str (HTML page), str(datestring)
        '''
        url = Scraper.construct_url(pos, fmt, 'rankings')
        return self.get_wayback(url, datestr)


class Parser():
    '''
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

    def _tr(self, tr, headers):
        '''
        Private method to parse tr element

        Args:
            tr: BeautifulSoup element
            headers: list of headers

        Returns:
            dict

        '''
        vals = [td.text.strip() for td in tr.find_all('td')]
        player = dict(zip(headers, vals))
        teams = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GB', 'HOU', 'IND', 'JAC',
                 'KC', 'LAC', 'LAR', 'MIA', 'MIN', 'NE', 'NO', 'NYG', 'NYJ', 'OAK', 'PHI', 'PIT', 'SD', 'SEA', 'SF',
                 'STL', 'TB', 'TEN', 'WAS']

        # player_id in <a href="#" class="fp-player-link fp-id-11645" fp-player-name="Le'Veon Bell"></a>
        a = tr.find('a', {'href': '#'})
        if a:
            player['source_player_id'] = a.attrs['class'][-1].split('-')[-1]
            player['player'] = a['fp-player-name']

        # team and bye in <small></small>
        for child in tr.findChildren():
            if child.name == 'small':
                if child.text.strip() in teams:
                    player['team_code'] = child.text.strip()
                else:
                    player['bye'] = child.text.strip().replace(')', '').replace('(', '')
        return player

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
        t = soup.find('table', {'id': 'rank-data'})
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
        headers = ['player', 'rush_att', 'rush_yds', 'rush_td', 'rcvg_rec', 'rcvg_yds', 'rcvg_tds', 'fl', 'fpts']
        if pos == 'QB':
            headers = ['player', 'pass_att', 'pass_cmp', 'pass_yds', 'pass_td', 'pass_int',
                       'rush_att', 'rush_yds', 'rush_td', 'fl', 'fpts']
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
            for k, v in zip(['best', 'worst', 'avg', 'stdev'], [td.text for td in tds[5:9]]):
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
            for k, v in zip(['best', 'worst', 'avg', 'stdev'], [td.text for td in tds[4:8]]):
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
        week = re.sub('[^0-9]', '', soup.select('div.subhead.pull-left')[0].text)

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
            rank['source_positional_rank'] = re.sub('[^0-9]', '', tds[2].text)
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


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()

    @staticmethod
    def pair_list(list_):
        '''
        Allows iteration over list two items at a time
        '''
        list_ = list(list_)
        return [list_[i:i + 2] for i in range(0, len(list_), 2)]

    def weekly_rankings_archived(self):
        '''
        Gets old fantasypros rankings from the wayback machine
        Uses wayback API to figure out if week rankings exist, then fetch+parse result

        Returns:
            players(list): of player rankings dict
        '''
        players = []
        base_fpros = 'https://www.fantasypros.com/nfl/rankings/{}.php'
        positions = ['QB', 'RB', 'WR', 'TE']

        # loop through seasons
        for season in [2014, 2015]:

            # s is dict with keys = week, dict with keys start, end as value
            s = get_season(season)

            # loop through weeks
            for week, v in s.items():
                if s.get(week, None):
                    weekdate = s.get(week)
                    if weekdate:
                        d = weekdate.get('start')
                        logging.debug('d is a {}'.format(type(d)))
                    else:
                        raise Exception('could not find start of {} week {}'.format(season, week))

                # loop through positions
                for pos in positions:

                    # generate url for wayback machine
                    fpros_url = base_fpros.format(pos)
                    content, cached = self._wb(fpros_url, d)

                    if content:
                        pw = self._p.weekly_rankings(content, season, week, pos)
                        logging.info(pw)
                        players.append(pw)
                    else:
                        logging.error('could not get {}|{}|{}'.format(season, week, pos))

                    if not cached:
                        time.sleep(2)

        # players is list of list, flatten at the end
        return list(itertools.chain.from_iterable(players))

    def weekly_rankings(self, season, week, flex=False):
        '''
        Gets current fantasypros rankings

        Returns:
            players(list): of player rankings dict
        '''
        # this doesn't work

        '''
        players = []
        base_fpros = 'https://www.fantasypros.com/nfl/rankings/{}.php'
        positions = ['qb', 'rb', 'wr', 'te', 'flex']

        # loop through seasons
        # loop through positions
        for pos in positions:
            if not flex and pos == 'flex':
                continue

            content = self._s.get(base_fpros.format(pos))

            if content:
                pw = self._p.weekly_rankings(content, season, week, pos)
                logging.info(pw)
                players.append(pw)
            else:
                logging.error('could not get {}|{}|{}'.format(season, week, pos))

        # players is list of list, flatten at the end
        if not flex:
            return list(itertools.chain.from_iterable(players))
        else:
            return list(itertools.chain.from_iterable(players)), flex_players
        '''

    def expert_weekly_rankings(self, season, week, pos, expert):
        '''
        Gets weekly rankings from expert

        Args:
            season:
            week:
            pos:
            expert:

        Returns:
            list: of dict

        '''
        # NOTE: should move this to a function
        # also need to figure out if can obtain old ones by week
        # step one: get the fantasypros list of players
        # then filter out lower-ranked players with ECR threshold
        posthresh = {'QB': 20, 'RB': 50, 'WR': 70, 'TE': 14, 'DST': 20, 'K': 14}
        pcontent = self._s.get_json(url='https://www.fantasypros.com/ajax/player-search.php',
                                    params={'sport': 'NFL', 'position_id': 'OP'})

        # add positional ranks and then filter by positional threshold
        playerdf = pd.DataFrame(pcontent)
        playerdf.drop(['filename', 'value'], axis=1, inplace=True)
        poscrit = playerdf['position'].isin(posthresh.keys())
        playerdf = playerdf[poscrit]
        playerdf.dropna(subset=['ecr'], inplace=True)
        playerdf['posrk'] = playerdf.groupby("position")["ecr"].rank()
        playerdf['thresh'] = playerdf['position'].apply(
            lambda x: posthresh.get(x, None))
        threshcrit = playerdf['posrk'] <= playerdf['thresh']
        playerdf = playerdf[threshcrit]
        playerdf.sort_values(by=['position', 'posrk'], inplace=True)

        # now do pairs of players
        compare_url = 'https://partners.fantasypros.com/api/v1/compare-players.php?'
        expert_ranks = []

        for pair in Agent.pair_list(playerdf.itertuples()):
            if (pair[0][4] != pair[1][4]):
                raise ValueError('pairs have different positions: {}'.format(pair))
            player_pair = '{}:{}'.format(pair[0][2], pair[1][2])
            pos = pair[0][4]

            # players are colon-separated ids (13926:16421)
            # expert 120 is Sean Koerner
            params = {
                'players': player_pair,
                'experts': expert,
                'position': pos,
                'ranking_type': '1',
                'details': 'all',
                'sport': 'NFL',
                'callback': 'FPWSIS.compareCallback'
            }

            content = self._s.get(url=compare_url, params=params)
            pair_rank = self._p.expert_rankings(content)
            expert_ranks.append(pair_rank)

        return expert_ranks


if __name__ == '__main__':
    pass
