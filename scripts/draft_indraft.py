#!/usr/bin/env python3

# draft_indraft.py
# script runs during draft
# generates dynamic page

import math
import os
from pathlib import Path
import sys
from time import sleep

import click
import webbrowser

try:
    from urllib import pathname2url
except:
    from urllib.request import pathname2url

import pandas as pd
from selenium import webdriver

from nfl.player.playerxref import *
from nfl.utility import getdb
from nflfantasy.parsers.draft import *
from nflfantasy.scrapers.draft import *


def draft_headers(key='draft'):
    '''
    Reads config file for DRAFT headers

    Returns:
        dict: of headers

    '''
    try:
        import ConfigParser as configparser
    except ImportError:
        import configparser
    config = configparser.ConfigParser()
    pth = Path.home() / '.draft'
    config.read(str(pth))

    return {'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Origin': 'https://draft.com',
        'Referer': 'https://draft.com/upcoming',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
        'X-Build-Number': '0',
        'X-Client-Sha': config.get(key, 'sha'),
        'X-Client-Type': 'web',
        'X-User-Auth-Id': config.get(key, 'auth'),
        'X-User-Token': config.get(key, 'token')}


def get_board(db, next_pick, ids):
    '''
    Gets remaining players in draft
    
    Args:
        db(NFLPostgres): db connection object
        next_pick(int): player's next pick
        ids(list): list of player ids that are already drafted
        col_order(list): list of columns to query

    '''
    ids = ','.join([str(i) for i in ids])
    q = """WITH adp AS (SELECT * FROM drbb.mvw_adp_vs_proj),
             x AS (SELECT player_id, source_player_id::int AS draft_player_id 
                   FROM base.player_xref WHERE source = 'draft'),
             pe AS (SELECT x.player_id, pe_1.pick, pe_1.prob
                    FROM drbb.mvw_probemp AS pe_1
                    LEFT JOIN x ON pe_1.player_id = x.draft_player_id)
             SELECT adp.plyr, adp.pos, adp.team, adp.npk, adp.adp, 
                    adp.my_ownpct, adp.valpg, pe.pick, pe.prob 
             FROM adp LEFT JOIN pe ON adp.player_id = pe.player_id
             WHERE pick = {} AND prob > .35 AND 
                   npk > 10 AND adp.player_id NOT IN ({})
             ORDER BY adp
             LIMIT 25"""
    return pd.read_sql(q.format(next_pick, ids), db.conn)


def html_table(fn, df, sort_index=4):
    '''
    Outputs an html table to disk

    Args:
        fn (str): filename to save
        df (DataFrame): the dataframe to create html from
        sort_index(int): column to sort by
        
    Returns:
        None

    '''
    # column 3 is adp, order asc
    # using plugin any-number to sort numeric columns - that is the "type" entry in columnDefs
    # use jquery script to alternate shading rows in white and grey
    # pandas creates a table that is plugged into the page
    # then write to /tmp/draft.html
    page = '''<!DOCTYPE html><html>
              <head>
                <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/dt-1.10.16/datatables.min.css"/>
              <body>
                  <script src="https://code.jquery.com/jquery-3.3.1.js"></script>
                  <script type="text/javascript" src="https://cdn.datatables.net/v/dt/dt-1.10.16/datatables.min.js"></script>
                  <script type="text/javascript" src="https://cdn.datatables.net/1.10.16/js/dataTables.bootstrap.min.js"></script>
                  <script type="text/javascript" src="https://cdn.datatables.net/plug-ins/1.10.18/sorting/any-number.js"></script>
                  <script type="text/javascript">
                    $(document).ready(function() {
                      $('#draft').DataTable( {
                        "iDisplayLength": 300,
                        "order": [|INDEX|, 'asc'],
                        "columnDefs": [
                            {"className": "dt-center", "targets": "_all"},
                            {"type": "any-number", "targets": [3,4,5,6,7,8]}
                          ]
                      } );
                    } );
                  </script>
                  <script type="text/javascript">
                  $(document).ready(function()
                    {$("tr:odd").css({
                     "background-color":"#cacfd2",
                     "color":"#000"});
                  });
                  </script>
                  |TABLE|
              </body>
              </html>'''

    # pandas 0.23 has improved API for generating tables
    # this code won't work in earlier versions of pandas
    html = df.to_html(border=0,
                      index=False,
                      classes=['compact', 'display'], 
                      table_id='draft')

    with open(fn, 'w') as outfile:
        page = page.replace('|TABLE|', html).replace('|INDEX|', str(sort_index))
        outfile.write(page)


def _next_pick(db, num_completed, draft_slot, num_teams):
    '''
    Gets next pick given number of completed picks and draft slot
    
    Args:
        num_completed(int): the number of completed picks
        draft_slot(int): starting draft position (1 to num_teams)
        num_teams(int): number of teams in draft

    Returns:
        int
        
    '''
    q = """SELECT pick FROM drbb.draft_round
           WHERE participants = {} AND pick_order = {} AND pick >= {}
           LIMIT 1"""
    return db.select_scalar(q.format(num_teams, draft_slot, num_completed))


@click.command()
@click.option('-d', '--draft_slot', type=int, help='your draft slot')
@click.option('-n', '--num_teams', type=int, help='number of teams in league')
@click.option('-l', '--league_id', type=str, help='DRAFT league id')
@click.option('-w', '--wait_time', type=int, default=20, help='Reload time interval')
def run(draft_slot, num_teams, league_id, wait_time):
    '''
    Ongoing script runs during draft

    Returns:
        None

    '''
    logging.basicConfig(level=logging.INFO)

    # use firefox driver to allow for auto-refresh 
    driver = webdriver.Firefox()
    db = getdb('nfl')
    ds = DraftNFLScraper(headers=draft_headers())
    dp = DraftNFLParser()
    player_draft_ids = player_draft(db)
    if wait_time > 30:
        num_loops = 300
    else:
        num_loops = (wait_time * 20) + 1

    for i in range(1, num_loops):
        draft = ds.draft(league_id=league_id)['draft']
        picks = dp.draft_picks(draft)
        
        # figure out when I'm going to be picking next
        # want to calculate % of player available at this pick
        # also want to filter out picked players and those
        # that have little chance of being there
        my_next_pick = _next_pick(db, len(picks), draft_slot, num_teams)
        already_picked_ids = [player_draft_ids.get(p['player_id']) 
               for p in picks if player_draft_ids.get(p['player_id'])]

        # get dataframe showing availability at next pick
        col_order = ['plyr', 'pos', 'team', 'npk', 'adp', 
                     'my_ownpct', 'valpg', 'pick', 'prob']
        df = get_board(db, my_next_pick, already_picked_ids)
        
        # now write temporary file
        fn = '/tmp/draft.html'
        html_table(fn, df[col_order], 4)

        # the webdriver API allows refresh
        # so once created Firefox window, don't need to relaunch   
        if i ==1:
            url = 'file:{}'.format(pathname2url(os.path.abspath(fn)))
            driver.get(url)
        else:
            driver.refresh()

        # in fast draft, want to wait ~ 20
        # in slow draft, no need to constantly update
        if num_loops == 0:
            term = input('Would you like to continue?')
            if term in ('y', 'Y', 'yes', 'Yes'):
                sys.exit()
        else:    
            sleep(wait_time)


if __name__ == '__main__':
    run()
