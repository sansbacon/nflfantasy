from multiprocessing import Pool, cpu_count
from bs4 import BeautifulSoup


conv = {'std': 'fantasy_points_std', 
        'ppr': 'fantasy_points_ppr', 
        'hppr': 'fantasy_points_hppr', 
        'dk': 'draftkings_points',
        'fd': 'fanduel_points', 
        'yh': 'yahoo_points'}

fmt = {'dk': 'FantasyPointsDraftKings', 
      'std': 'FantasyPoints', 
      'ppr': 'FantasyPointsPPR',
      'fd': 'FantasyPointsFanDuel',
      'yh': 'FantasyPointsYahoo',
      'hppr': 'FantasyPointsHalfPointPpr'
}

seas = {'0': 2017, '1': 2016, '2': 2015, '3': 2014}

def _row(tr):
    '''
    Parses one row of table for fantasydata weekly results

    Args:
        tr(BeautifulSoup.element): row element in table
        
    '''
    vals = [td.text.strip() for td in tr.find_all('td')]
    href = tr.find('a')['href']
    parts = href.split('=')[-1].split('-')
    player_id = parts[0]
    return {
      'source': 'fantasydata',
      'source_player_id': parts[0],
      'source_player_code': '-'.join(parts[1:]),
      'source_player_name': vals[1],
      'source_player_position': vals[2],
      'source_team_id': vals[4],
      'rec': vals[11],
      'fpts': vals[-1]
    }


def _fpts(vals, fmt):
    '''
    Calculates fantasy points from vals
    
    '''
    (float(vals[6]) * .04) + (float(vals[7])*4) - float(vals[8]) + \
    (float(vals[9]) * .10) + (float(vals[10]) * 6) + (float(vals[12]) * .10) + \
    (float(vals[13] * 6)) - (2 * float(vals[14]))
    print(tot)
    if fmt == 'hppr':
        tot += float(vals[11]) * .5
    elif fmt == 'ppr':
        tot += float(vals[11])
    return tot

        
def _hppr(se):
    results = []
    for week in range(17):
        for team in range(1,33):
            team_players = {}
            key = '{}-{}-{}-{}'.format(se, week, team, 'FantasyPoints')
            with open('/home/sansbacon/fantasydata/{}.htm'.format(key)) as f:
                soup = BeautifulSoup(f.read(), 'lxml')
            for tr in soup.find('table', {'id': 'StatsGrid'}).find_all('tr')[1:]:
                vals = [td.text.strip() for td in tr.find_all('td')]
                p = _row(tr)
                spid = p['source_player_id']
                p['season_year'] = seas.get(se)
                p['week'] = week + 1
                p['fantasy_points_hppr'] = _fpts(vals, 'hppr')
                p['fantasy_points_ppr'] = _fpts(vals, 'ppr') 
                team_players[spid] = p
            results.append(list(team_players.values()))
    return results


with Pool(cpu_count()) as p:
    #results = p.map(_hppr, [str(i) for i in range(4)])
    _hppr('0')
