'''
fpros_weekly
gets fpros rankings for range of weeks
arguments:
    --fmt
    --weekstart
    --weekend
    
usage:
    python fpros_weekly.py --fmt='ppr' --weekstart=1 --weekend=17
'''

import logging
import click

from nfl.names import match_player
from nfl.parsers.fantasypros import FantasyProsNFLParser
from nfl.player.fprosxref import fpros_players
from nfl.player.playerxref import nflcom_players
from nfl.scrapers.fantasypros import FantasyProsNFLScraper
from nfl.seasons import current_season_year
from nfl.utility import getdb


def _insp(db, vals):
    '''
    Inserts player into database
    
    Args:
        db:
        vals: 

    Returns:

    '''

    #wanted = ['source', 'source_player_id', 'source_player_name', 'source_last_updated',
    #          'source_player_position', 'season_year', 'week', 'source_player_team',
    #          'source_player_opp', 'rank', 'avg', 'best', 'worst', 'stdev',]

    numeric_fields = ['avg', 'best', 'rank', 'stdev', 'worst']

    for player in vals:
        p = {}
        for k,v in player.items():
            if k == 'source_player_posrk':
                continue
            elif k in numeric_fields:
                try:
                    p[k] = float(v)
                except:
                    p[k] = 0
            elif (v == '' or v == '-'):
                p[k] = None
            else:
                p[k] = v

        table_name = 'extra_fantasy.weekly_rankings'
        placeholders = ', '.join(['%s'] * len(p))
        columns = ', '.join(list(p.keys()))
        sql = """INSERT INTO %s ( %s ) VALUES ( %s )
               ON CONFLICT ON CONSTRAINT weekly_rankings_source_season_year_week_source_player_id_fmt_ke 
               DO UPDATE SET (rank, avg, best, worst, stdev, source_last_updated) = 
               (EXCLUDED.rank, EXCLUDED.avg, EXCLUDED.best, EXCLUDED.worst, EXCLUDED.stdev, EXCLUDED.source_last_updated);
               """ % (table_name, columns, placeholders)

        with db.conn.cursor() as cursor:
            try:
                cursor.execute(sql, list(p.values()))
                db.conn.commit()
            except Exception as e:
                logging.exception('insert_dict failed: {0}'.format(e))
                db.conn.rollback()

def _get_nflcom_id(r, fpp, nflp):
    '''
    Finds nflcom_id through multiple methods
    
    Returns:
        str: nflcom_player_id
    '''
    nflcom_id = None

    # first see if already in player_xref table
    match = fpp.get(r['source_player_id'])
    if match:
        nflcom_id = match

    # if not in player_xref table, then try direct match
    # if no direct match, then try fuzzy match
    else:
        key = '{}_{}'.format(r['source_player_name'], r['source_player_position'])
        match = nflp.get(key)
        if match:
            nflcom_id = match[0]['player_id']
            if len(match) > 1:
                logging.warning('have multiple matches for {}'.format(key))
        else:
            match = nflp.get(match_player(key, list(nflp.keys())))
            if match:
                if len(match) == 1:
                    nflcom_id = match[0]['player_id']
                else:
                    logging.warning('have multiple matches for {}'.format(key))
            else:
                logging.warning('no matches for {}'.format(key))

    return nflcom_id

@click.command()
@click.option('--weekstart')
@click.option('--weekend')
@click.option('--fmt', default='ppr')
@click.option('--position', default='all')
def run(fmt, weekstart, weekend, position):
    '''
    Gets fantasypros ranks for range of weeks and positions    
    Args:
        fmt: 
        weekstart: 
        weekend: 
        position: 

    Returns:
        list, list
    '''
    db = getdb()
    parser = FantasyProsNFLParser()
    scraper = FantasyProsNFLScraper(cache_name='fpros', delay=1)

    # get existing fantasypros players and nflcom players
    fpp = fpros_players(db)
    nflp = nflcom_players(db)

    # can pass pipe-delimited list of positions
    if position == 'all':
        positions = ['qb', 'wr', 'te', 'rb', 'flex', 'dst', 'k']
    elif '|' in position:
        positions = position.split('|')
    else:
        positions = [position]

    # returns players and flex
    players = []
    flex = []

    # loop through weeks and positions
    for week in range(int(weekstart), int(weekend)+1):
        logging.info('starting {}'.format(week))
        for pos in positions:
            logging.info('starting {}'.format(pos))
            content = scraper.weekly_rankings(pos, fmt, week)
            ranks = parser.weekly_rankings(content=content, fmt=fmt, pos=pos,
                                           season_year=current_season_year(), week=week)

            # now add nflcom player ids
            for idx, r in enumerate(ranks):
                ranks[idx]['nflcom_player_id'] = _get_nflcom_id(r, fpp, nflp)

            # add to list and database
            if pos in ['flex', 'FLEX']:
                flex = ranks
            else:
                players += ranks
            _insp(db, ranks)
            logging.info('{} finished week {}'.format(pos, week))

    return players, flex


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    run()