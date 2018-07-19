# goal is to see the relationship between
# QB performance and his RB, WR, TE

# step one: get top 5 QB for every week
# from 2013-2017
# fields: seas, week, nflcom_player_id, source, source_player_name,
#         pos, team, fpts_ppr, 
#         wr_rks, wr_fpts_ppr, wr_ids, wr_nflids, wr_names,
#         rb_rks, rb_fpts_ppr, rb_ids, rb_nflids, rb_names,
#         te_rks, te_fpts_ppr, te_ids, te_nflids, te_names

from multiprocessing import Pool, cpu_count

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


def scrape():
    q = """select * from extra_fantasy.vw_qb_top5"""
    qbs = db.select_dict(q)

    ## problem: dataset is not complete
    ## nulls

    ## solution #1: get data from another source
    url = 'https://fantasydata.com/nfl-stats/nfl-fantasy-football-stats.aspx?fs=3&stype=0&sn=1&scope=1&w=0&ew=0&s=&t=1&p=1&st=FantasyPointsDraftKings&d=1&ls=&live=false&pid=false&minsnaps=4'
    params = { 
     'd': '1',
     'ew': '0',
     'fs': '3',
     'live': 'false',
     'minsnaps': '4',
     'p': '1',
     'pid': 'false',
     'scope': '1',
     'sn': '1',
     'st': 'FantasyPointsDraftKings',
     'stype': '0',
     't': '1',
     'w': '0'
    }

    # t = team_id, starts at 1 (ARI), goes through 32 (WAS)
    # w, ew: starting and ending weeks (uses 0 index, so week 1 = 0)
    # sn: season (uses 0 index, 2017 = 0 and so forth)
    # st: scoring formats
    import random
    import time
    from urllib.parse import urlencode 

    from nflmisc.scraper import FootballScraper
    from nflutility import *

    s = FootballScraper(cache_name='fantasydata')
    vals = {}
    base_url = 'https://fantasydata.com/nfl-stats/nfl-fantasy-football-stats.aspx?'
    for season in range(6):
        for week in range(17):
            for team in range(1,33):
                for scoring_format in fmt.values():
                    key = '{}-{}-{}-{}'.format(season, week, team, scoring_format)       
                    print('got {}'.format(key))
                    params = { 
                         'd': '1',
                         'ew': week,
                         'fs': '3',
                         'live': 'false',
                         'minsnaps': '4',
                         'p': '1',
                         'pid': 'false',
                         'scope': '1',
                         'sn': season,
                         'st': scoring_format,
                         'stype': '0',
                         't': team,
                         'w': week
                    }
                    qs = urlencode(sorted(params.items(), key=lambda x: x[0]))
                    content = s.get_filecache(base_url + qs.encode('utf-8'))
                    vals[key] = content
                    print('got {}'.format(key))
                    time.sleep(random.randint(1, 5)*random.random())
                    
    save_file(vals, '/home/sansbacon/fantasydata.pkl')


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
      'rec': vals[],
      'fpts': vals[-1]
    }


def _season(se):
    '''
    One season of data
    '''
    results = []
    for week in range(17):
        for team in range(1,33):
            team_players = {}
            for scoring_format in ['std', 'ppr', 'hppr', 'dk', 'fd', 'yh']:
                key = '{}-{}-{}-{}'.format(se, week, team, fmt.get(scoring_format))
                with open('/home/sansbacon/fantasydata/{}.htm'.format(key)) as f:
                    soup = BeautifulSoup(f.read(), 'lxml')
                for tr in soup.find('table', {'id': 'StatsGrid'}).find_all('tr')[1:]:
                    p = _row(tr)
                    spid = p['source_player_id']
                    pts_type = conv.get(scoring_format)
                    p['season_year'] = seas.get(se)
                    p['week'] = week + 1
                    # if there is a match, you want to merge the dicts
                    # otherwise just add the dict
                    match = team_players.get(spid)
                    if match:
                        team_players[spid][pts_type] = p['fpts'] 
                    else:
                        team_players[spid] = p
                   
            results.append(list(team_players.values()))
    return results
    
def run():
    with Pool(cpu_count()) as p:
        results = p.map(_season, [str(i) for in in range(4)])
            
