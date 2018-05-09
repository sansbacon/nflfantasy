# dklobby.py

import datetime
import json
import logging
import os
import re

def dk_lobby(content, season, week):
    '''
    Parses dk lobby (json embedded in HTML page) and returns list of contest dicts

    Args:
        content(str): HTML from lobby
        season (int):
        week (int): for football only

    Returns:
        contests(list): of contest dicts
    '''
    contests = []
    pattern = re.compile(r'packagedContests = (\[.*?\])\;', re.MULTILINE | re.DOTALL)
    match = re.search(pattern, content)

    if match:
        for contest in json.loads(match.group(1)):
            # 1 - NFL, 2- MLB, NBA??
            if contest.get('s') == 1:
                # convert epoch string to date
                ds = re.findall('\d+', contest.get('sd', ''))[0]
                cd = datetime.datetime.strftime(datetime.datetime.fromtimestamp(float(ds)/1000), '%m-%d-%Y')

                # create context dict
                headers = ['season', 'week', 'contest_name', 'contest_date', 'contest_slate', 'contest_fee', 'contest_id', 'max_entries', 'contest_size', 'prize_pool']
                vals = [season, week, contest.get('n'), cd, contest.get('sdstring'), contest.get('a'), contest.get('id'), contest.get('mec'), contest.get('m'), contest.get('po')]
                contests.append(dict(zip(headers, vals)))

    return contests

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    from nfl.db.nflpg import NFLPostgres
    nflp = NFLPostgres(database='nfl', user=os.environ['NFLPGUSER'], password=os.environ['NFLPGPASSWORD'])
    with open('/home/sansbacon/workspace/nfl/parsers/dklobby.html', 'r') as infile:
        contests = dk_lobby(infile.read(), 2016, 1)
        nflp.insert_dicts(contests, 'dk_contests')
