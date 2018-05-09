import copy
import logging
import os
import pprint
import random
import time

import dateparser
from bs4 import BeautifulSoup
import requests
import requests_cache


def implied(ou, spread):
    return (ou - spread) / float(2)


def parse(content, extras):
    teams = []
    soup = BeautifulSoup(content, 'lxml')
    t = soup.find('table', class_='table')

    if t:
        thead = t.find('thead')
        cols = [thd.string.lower().strip().replace(' ', '_') for thd in thead.findAll('th')]
        tb = t.find('tbody')

        for tr in tb.findAll('tr'):
            vals = [td.text.strip().replace(u'\xa0', u'').replace('\r\n', '') for td in tr.findAll('td')]
            team = (dict(zip(cols, vals)))
            for k, v in extras.items(): team[k] = v
            teams.append(team)

    return teams


def fix(games):
    '''
    Replace N/A with none
    Alter date field so it can be converted to datetime
    '''

    fixed = []
    exclude = ['away_ml', 'home_ml']

    for game in games:
        # no values for away_ml, home_ml
        g2 = copy.deepcopy(game)

        for k, v in game.items():
            # convert to datetime
            if k.lower() == 'date':
                parts = v.split('   ')
                g2['game_date'] = dateparser.parse(parts[0].strip())
                g2.pop('date')

            # replace N/A with None
            if v == 'N/A':
                g2[k] = None

                # create home_team and away_team fields
            # calculate implied totals
            if k.lower() == 'favorite':
                if v[0:3] == 'at ':
                    g2['home_team'] = team_names(v[3:])
                    g2['away_team'] = team_names(game.get('underdog'))
                    g2['away_total'] = implied(float(game.get('total')), 0 - float(game.get('spread')))
                    g2['home_total'] = implied(float(game.get('total')), float(game.get('spread')))

                else:
                    g2['home_team'] = team_names(game.get('underdog')[3:])
                    g2['away_team'] = team_names(v)
                    g2['home_total'] = implied(float(game.get('total')), 0 - float(game.get('spread')))
                    g2['away_total'] = implied(float(game.get('total')), float(game.get('spread')))

        fixed.append(g2)

    return fixed


def team_names(name):
    names = {'Arizona': 'ARI', 'Atlanta': 'ATL', 'Baltimore': 'BAL', 'Buffalo': 'BUF', 'Carolina': 'CAR',
             'Chicago': 'CHI', 'Cincinnati': 'CIN', 'Cleveland': 'CLE', 'Dallas': 'DAL', 'Denver': 'DEN',
             'Detroit': 'DET', 'Green Bay': 'GB', 'Houston': 'HOU', 'Indianapolis': 'IND', 'Jacksonville': 'JAC',
             'Kansas City': 'KC', 'Miami': 'MIA', 'Minnesota': 'MIN', 'New England': 'NE', 'New Orleans': 'NO',
             'NY Giants': 'NYG', 'NY Jets': 'NYJ', 'Oakland': 'OAK', 'Philadelphia': 'PHI', 'Pittsburgh': 'PIT',
             'San Diego': 'SD', 'San Francisco': 'SF', 'Seattle': 'SEA', 'St. Louis': 'STL', 'Tampa Bay': 'TB',
             'Tennessee': 'TEN', 'Washington': 'WAS', 'JACK': 'JAC', 'WSH': 'WAS', 'Cardinals': 'ARI', 'Falcons': 'ATL',
             'Ravens': 'BAL', 'Bills': 'BUF', 'Panthers': 'CAR', 'Bears': 'CHI', 'Bengals': 'CIN', 'Browns': 'CLE',
             'Cowboys': 'DAL', 'Broncos': 'DEN', 'Lions': 'DET', 'Packers': 'GB', 'Texans': 'HOU', 'Colts': 'IND',
             'Jaguars': 'JAC', 'Chiefs': 'KC', 'Dolphins': 'MIA', 'Vikings': 'MIN', 'Patriots': 'NE', 'Saints': 'NO',
             'Giants': 'NYG', 'Jets': 'NYJ', 'Raiders': 'OAK', 'Eagles': 'PHI', 'Steelers': 'PIT', 'Chargers': 'SD',
             '49ers': 'SF', 'Seahawks': 'SEA', 'Rams': 'STL', 'Buccaneers': 'TB', 'Titans': 'TEN', 'Redskins': 'WAS',
             'Buffalo Bills': 'BUF', 'Seattle Seahawks': 'SEA', 'Philadelphia Eagles': 'PHI', 'St. Louis Rams': 'STL',
             'Arizona Cardinals': 'ARI', 'Carolina Panthers': 'CAR', 'Green Bay Packers': 'GB',
             'New England Patriots': 'NE', 'Dallas Cowboys': 'DAL', 'Detroit Lions': 'DET', 'Kansas City Chiefs': 'KAN',
             'Houston Texans': 'HOU', 'Baltimore Ravens': 'BAL', 'New York Giants': 'NYG', 'Denver Broncos': 'DEN',
             'Chicago Bears': 'CHI', 'Miami Dolphins': 'MIA', 'San Francisco 49ers': 'SAN', 'Cincinnati Bengals': 'CIN',
             'Cleveland Browns': 'CLE', 'Indianapolis Colts': 'IND', 'Minnesota Vikings': 'MIN',
             'Washington Redskins': 'WAS', 'Jacksonville Jaguars': 'JAC', 'Pittsburgh Steelers': 'PIT',
             'Atlanta Falcons': 'ATL', 'New Orleans Saints': 'NO', 'Tennessee Titans': 'TEN',
             'Tampa Bay Buccaneers': 'TB', 'New York Jets': 'NYJ', 'Oakland Raiders': 'OAK', 'San Diego Chargers': 'SD'}
    return names.get(name)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    requests_cache.install_cache('lines_cache', allowable_methods=('GET', 'POST'))

    games = []
    seasons = range(2002, 2016)
    weeks = range(1, 18)
    base_url = 'https://fantasydata.com/nfl-stats/nfl-point-spreads-and-odds.aspx'

    # ctl00$ctl00$Body$Body$Season = 2014
    # ctl00$ctl00$Body$Body$SeasonType = 1
    # ctl00$ctl00$Body$Body$Week = 16

    payload = {
        'ctl00$ctl00$Body$Body$SeasonType': 1,
    }

    for season in seasons:
        for week in weeks:
            try:
                payload['ctl00$ctl00$Body$Body$Season'] = season
                payload['ctl00$ctl00$Body$Body$Week'] = week
                r = requests.post(base_url, data=payload)
                r.raise_for_status()

                fn = 'odds_{season}_{week}.html'.format(season=season, week=week)

                if not os.path.isfile(fn):
                    with open(os.path.join(os.path.expanduser('~'), fn), 'w') as outfile:
                        outfile.write(r.content)

                if r.from_cache:
                    logging.debug('got from cache')
                else:
                    logging.debug('not from cache')
                    time.sleep(1)

                games += parse(r.content, extras={'season': season, 'week': week})

            except Exception as e:
                logging.exception(e)

    games = fix(games)
    pprint.pprint(random.sample(games, 10))