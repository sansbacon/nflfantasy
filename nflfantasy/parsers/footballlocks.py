from collections import defaultdict
import logging

from bs4 import BeautifulSoup as bs
from nfl.teams import city_to_code


class FootballLocksNFLParser():
    '''
    FootballLocksNFLParser

    Usage:

    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _fix_odds(self, o):
        '''

        Args:
            o(dict): dictionary of odds

        Returns:
            o(dict): add keys to dict

        '''
        fav = o.get('favorite')
        dog = o.get('underdog')

        # tot won't convert if empty
        tot = o.get('total', 0)
        try:
            tot = float(tot)
        except:
            tot = 0
        o['game_total'] = tot

        # spread won't convert if PK or empty
        spread = o.get('spread', 0)
        if spread == 'PK' or spread == '':
            spread = 0
        else:
            try:
                spread = float(spread)
            except:
                spread = 0
        o['spread'] = spread

        # home favorite has 'At' before city name
        if 'At' in fav:
            home_team = ' '.join(fav.split(' ')[1:])
            away_team = dog
            home_total = self._implied_total(tot, spread)
            away_total = tot - home_total

        else:
            away_team = fav
            home_team = ' '.join(dog.split(' ')[1:])
            away_total = self._implied_total(tot, spread)
            home_total = tot - away_total

        o['home_team'] = city_to_code(home_team)
        o['away_team'] = city_to_code(away_team)
        o['home_implied'] = home_total
        o['away_implied'] = away_total

        wanted = ['season_year', 'week', 'dt', 'away_team', 'home_team', 'away_implied', 'home_implied', 'game_total', 'spread', 'money_odds']
        return {k:v for k,v in o.items() if k in wanted}

    def _implied_total(self, game_total, spread):
        '''
        Takes game total and spread and returns implied total based on those values

        Args:
            game_total (float): something like 53.5
            spread (float): something like -1.5

        Returns:
            implied_total (float): something like 27.5
        '''

        try:
            return (float(game_total) / 2) - (float(spread) / 2)

        except TypeError, e:
            logging.error('implied total error: {0}'.format(e.message))
            return None

    def odds(self, content, season_start, week):
        '''
        Parses HTML page of odds
        Args:
            content(str): page for week of odds, has several years in separate tables

        Returns:

        '''
        season = season_start
        results = []
        soup = bs(content, 'lxml')

        # there are 2 different kinds of tables: main slate & MNF except for week 17
        # that is why I need to process main + MNF as a pair
        tables = soup.find_all('table', {'cols': '6', 'cellspacing': '6'})
        headers = ['dt', 'favorite', 'spread', 'underdog', 'total', 'money_odds']

        if week == 17:
            for t in tables:
                for tr in t.find_all('tr')[1:]:
                    val = dict(zip(headers, [td.text.strip() for td in tr.find_all('td')]))
                    val['season_year'] = season_start
                    val['week'] = week
                    results.append(self._fix_odds(val))
                    season -= 1

        else:
            i = 0
            while i < len(tables):
                # do the main table first
                main = tables[i]
                for tr in main.find_all('tr')[1:]:
                    val = dict(zip(headers, [td.text.strip() for td in tr.find_all('td')]))
                    val['season_year'] = season
                    val['week'] = week
                    results.append(self._fix_odds(val))

                mnf = tables[i + 1]
                for tr in mnf.find_all('tr'):
                    val = dict(zip(headers, [td.text.strip() for td in tr.find_all('td')]))
                    val['season_year'] = season
                    val['week'] = week
                    results.append(self._fix_odds(val))

                i += 2
                season -= 1

        return results

    '''
    def test_get(self):
        url = 'http://www.footballlocks.com/nfl_odds_week_1.shtml'
        content = self.s.get(url)
        self.assertIsNotNone(content)
        self.assertIsInstance(content, basestring)

    def test_parse(self):
        url = 'http://www.footballlocks.com/nfl_odds_week_1.shtml'
        content = self.s.get(url)
        soup = BS(content, 'lxml')
        for t in soup.find_all('table', {'width': 644, 'cellspacing': 0, 'cellpadding': 3}):
            print('match')

        for t in soup.find_all('table', {'cols': 6, 'width': 644, 'cellspacing': 6, 'border': 0}):
            print('match 2')

    def fix_odds(self, o):
        h = {'season_year': int(o['season_year']), 'week': int(o['week'])}
        v = {'season_year': int(o['season_year']), 'week': int(o['week'])}
        try:
            gd = o['game_date'].split(' ')[0] + '/' + str(o['season_year'])
            gd = convert_format(gd, 'nfl')
            h['game_date'] = gd
            v['game_date'] = gd
        except:
            h['game_date'] = datetostr(o['game_date'], 'nfl')
            v['game_date'] = h['game_date']
        try:
            fav = o['favorite']
            dog = o['underdog']

            if '(' in fav:
                h['team_code'] = city_to_code(fav.split('(')[0])
                h['opp'] = city_to_code(dog)
                if (o.get('line', None) == 'PK'):
                    o['line'] = 0
                h['consensus_spread'] = float(o['line'])
                h['consensus_game_ou'] = float(o['total'])
                v['team_code'] = h['opp']
                v['opp'] = h['team_code']
                v['consensus_spread'] = 0 - float(o['line'])
                v['consensus_game_ou'] = float(o['total'])

            elif '(' in dog:
                h['opp'] = city_to_code(fav)
                h['team_code'] = city_to_code(dog.split('(')[0])
                if (o.get('line', None) == 'PK'):
                    o['line'] = 0
                h['consensus_spread'] = 0 - float(o['line'])
                h['consensus_game_ou'] = float(o['total'])
                v['opp'] = h['team_code']
                v['team_code'] = h['opp']
                v['consensus_spread'] = float(o['line'])
                v['consensus_game_ou'] = float(o['total'])

            elif 'At ' in fav:
                h['team_code'] = city_to_code(fav.split('At ')[-1])
                h['opp'] = city_to_code(dog)
                if (o.get('line', None) == 'PK'):
                    o['line'] = 0
                h['consensus_spread'] = float(o['line'])
                h['consensus_game_ou'] = float(o['total'])
                v['team_code'] = h['opp']
                v['opp'] = h['team_code']
                v['consensus_spread'] = 0 - float(o['line'])
                v['consensus_game_ou'] = float(o['total'])

            elif 'At ' in dog:
                h['opp'] = city_to_code(fav)
                h['team_code'] = city_to_code(dog.split('At ')[-1])
                if (o.get('line', None) == 'PK'):
                    o['line'] = 0
                h['consensus_spread'] = 0 - float(o['line'])
                h['consensus_game_ou'] = float(o['total'])
                v['opp'] = h['team_code']
                v['team_code'] = h['opp']
                v['consensus_spread'] = float(o['line'])
                v['consensus_game_ou'] = float(o['total'])

        except Exception as e:
            print(e)

        return [h, v]

    def test_season(self):
        q = """
        INSERT INTO gamesmeta (season_year, week, game_date, team_code, opp, consensus_spread, consensus_game_ou)
        VALUES ({}, {}, '{}', '{}', '{}', {}, {});
        """
        url = 'http://www.footballlocks.com/nfl_odds_week_{}.shtml'
        for w in range(3,18):
            headers = ['game_date', 'favorite', 'line', 'underdog', 'total']
            content = self.s.get(url.format(w))
            patt = re.compile(r'Monday Night Football.*?(<TABLE.*?</TABLE>)', re.MULTILINE | re.DOTALL)
            match = re.search(patt, content)
            if match:
                soup = BS(match.group(1), 'lxml')
                trs = soup.find_all('tr')
                for tr in trs[1:]:
                    vals = [td.text.strip() for td in tr.find_all('td')][:-1]
                    d = dict(zip(headers, vals))
                    d['season_year'] = 2016
                    d['week'] = w
                    for i in self.fix_odds(d):
                        print q.format(i['season_year'], i['week'], i['game_date'],
                                       i['team_code'], i['opp'], i['consensus_spread'], i['consensus_game_ou'])

    '''

if __name__ == "__main__":
    pass