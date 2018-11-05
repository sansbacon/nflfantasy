from collections import defaultdict
import logging
import re

from bs4 import BeautifulSoup

from nflmisc.scraper import FootballScraper


class Scraper(FootballScraper):
    '''

    '''
    def adp(self, fmt='ppr', teams=12):
        '''
        Gets ADP page from fantasyfootballcalculator

        Args:
            fmt:
            teams:

        Returns:
            HTML string or None
        '''
        url = 'https://fantasyfootballcalculator.com/adp_xml.php?'
        params = {'format': fmt, 'teams': teams}
        return self.get(url, payload=params)

    def adp_old(self, season_year, fmt='ppr'):
        '''
        Gets ADP page from fantasyfootballcalculator

        Args:
            fmt:
            teams:

        Returns:
            HTML string or None
        '''
        url = 'https://fantasyfootballcalculator.com/adp?'
        params = {'year': season_year, 'format': fmt, 'teams': '12', 'view': 'graph', 'pos': 'all'}
        return self.get(url, payload=params)

    def projections(self):
        '''
        Fetch projections/rankings

        Args:
            url (str): url for the fantasy football calculator projections page

        Returns:
            HTML string if successful, None otherwise.
        '''
        url = 'https://fantasyfootballcalculator.com/rankings'
        return self.get(url)


class Parser():
    '''
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.positions = ['QB', 'RB', 'WR', 'TE']

    def _fix_header(self, header):
        '''
        Looks at global list of headers, can provide extras locally
        :param headers:
        :return:
        '''

        fixed = {
            'id': 'ffcalculator_id',
            'rk': 'overall_rank',
            'avg': 'fantasy_points_per_game',
        }

        # return fixed.get(header, header)
        fixed_header = self._fix_header(header)

        # fixed_header none if not found, so use local list
        if not fixed_header:
            return fixed.get(header, header)

        else:
            return fixed_header

    def _fix_headers(self, headers):
        '''

        :param headers:
        :return:
        '''
        return [self.fix_header(header) for header in headers]

    def _to_overall_pick(self, adp, adp_league_size, my_league_size):
        '''
        Data is in 2.01 format, so you have to translate those numbers to an overall pick

        :param adp(str): is in round.pick format
        :param adp_league_size(int): number of teams in types of draft (8, 10, 12, 14)
        :return: Dictionary: is overall, round, pick based on your league size
        '''
        round, pick = adp.split('.')
        overall_pick = ((int(round) - 1) * adp_league_size) + int(pick)
        adjusted_round = math.ceil(overall_pick / float(my_league_size))
        if adjusted_round == 1:
            adjusted_pick = overall_pick
        else:
            adjusted_pick = overall_pick - ((adjusted_round - 1) * my_league_size)
        return {'overall_pick': overall_pick, 'round': adjusted_round, 'pick': adjusted_pick}

    def adp_old(self, content):
        '''
        Gets ADP from past seasons

        Args:
            content:

        Returns:
            list of dict
        '''
        results = []
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', class_=['table', 'adp'])
        headers = ['rank', 'pick', 'source_player_name', 'pos', 'team_code', 'overall', 'stdev', 'high', 'low', 'n']
        for tr in t.find_all('tr'):
            if tr.has_attr('class'):
                vals = [td.text for td in tr.find_all('td')[:-1]]
                results.append(dict(zip(headers, vals)))
            else:
                pass

        return results

    def adp(self, xml, size=12):
        '''
        Parses xml and returns list of player dictionaries
        Args:
            content (str): xml typically fetched by FantasyCalculatorNFLScraper class
        Returns:
            List of dictionaries if successful, empty list otherwise.
        '''
        players = []
        root = ET.fromstring(xml)
        adp_league_size = int(root.find('.//teams').text)
        for item in root.findall('.//player'):
            if item.find('./pos').text.lower() == 'pk':
                pass
            else:
                player = {'source': 'ffcalc'}
                for child in item.findall('*'):
                    if child.tag.lower() == 'adp':
                        fixed = self._to_overall_pick(child.text, adp_league_size, size)
                        player['overall_pick'] = fixed['overall_pick']
                        player['round'] = int(fixed['round'])
                        player['pick'] = int(fixed['pick'])
                    else:
                        player[child.tag.lower()] = child.text
                players.append(player)
        return players

    def projections(self, content):
        '''
        Parses all rows of html table using BeautifulSoup and returns list of player dictionaries
        Args:
            content (str): html table typically fetched by FantasyCalculatorNFLScraper class
        Returns:
            List of dictionaries if successful, empty list otherwise.
        '''

        players = []
        headers = []

        soup = BeautifulSoup(content)
        table = soup.find('table', {'id': 'rankings-table'})

        for th in table.findAll('th'):
            value = th.string.lower()

            if re.match(r'\d+', value):
                headers.append('week%s_projection' % value)
            else:
                headers.append(value)

        headers = self.fix_headers(headers)

        # players - use regular expression to include header row (which has no class)
        for row in table.findAll('tr', {'class': re.compile(r'\w+')}):
            self.logger.debug(row)
            tds = [td.string for td in row.findAll("td")]
            player = dict(zip(headers, tds))

            # exclude unwanted positions from results
            if player.get('position') in self.positions:
                players.append(player)
            else:
                self.logger.info('excluded %s because %s' % (player.get('full_name'), player.get('position')))

        return players

    def draftboard(self, content):
        '''
        Parses HTML draftboard

        Args:
            content(str): HTML page

        Returns:
            dict

        '''
        html = HTML(html=content)

        # draft metadata
        # format, draft #, time/date
        draft = {}
        fmts = {'PPR Mock Draft': 'ppr',
                '2-QB Mock Draft': '2qb',
                'Standard Mock Draft': 'std',
                'Dynasty Mock Draft': 'dyn'}
        h1 = html.find('h1', first=True)
        draft['fmt'] = fmts.get(h1.text)
        for p in html.find('p'):
            if 'Draft #' in p.text:
                draft['dn'], draft['td'] = [item.strip() for item in p.text.split('; ')]
                break

        # get number/type of teams
        thead = html.find('#draftboardHead', first=True)
        drafters = {}
        for th in thead.find('tr', first=True).find('th'):
            if 'roundColBlank' in th.attrs.get('class', ''):
                continue
            elif th.text not in [str(i) for i in range(0, 15)]:
                continue
            elif 'computer' in th.attrs.get('class', ''):
                drafters[int(th.text)] = 'computer'
            else:
                drafters[int(th.text)] = 'human'
        draft['drafters'] = drafters

        # now go through picks
        # first cell in row is round number
        # then each cell after that is a single pick
        picks = defaultdict(dict)
        patt = re.compile('\(([A-Z]+)\)')
        for rnd, tr in enumerate(html.find('#draftboardBody', first=True).find('tr')):
            for idx, td in enumerate(tr.find('td')):
                if idx == 0:
                    round = int(td.text)
                else:
                    a = td.find('a', first=True)
                    p = {'name': a.attrs.get('title'),
                         'href': a.attrs.get('href'),
                         'pos': td.attrs.get('class')[0]}

                    # team is *current* team, not the team
                    # at the time of the draft
                    # will have to backfill this but it could
                    # be useful for matching purposes
                    match = re.search(patt, td.text)
                    if match:
                        p['current_team'] = match.group(1)
                    picks[rnd + 1][idx] = p
        draft['picks'] = picks
        return draft


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()



if __name__ == '__main__':
    pass
