# coding: utf-8
'''
Parses dk salaries file
Gets ffnerd projections or fantasypros ranks
Compares salary rank to projection or consensu rank by position
'''

import functools
import logging
import os
import random

import click
import pandas as pd

from fuzzywuzzy import process

from nfl.parsers.ffnerd import FFNerdNFLParser
from nfl.parsers.fantasypros import FantasyProsNFLParser
from nfl.scrapers.ffnerd import FFNerdNFLScraper
from nfl.scrapers.fantasypros import FantasyProsNFLScraper


def dkplayers(contestfn):
    '''
    Parses dkcontest file, which has player salaries
    Args:
        contestfn: 

    Returns:

    '''
    players = []
    contestheaders = ['position', 'name_ID', 'name', 'ID', 'salary', 'game', 'team']
    with open(contestfn, 'r') as infile:
        for line in infile.readlines()[7:]:
            cells = [c.strip() for c in line.split(',')[14:] if len(c) >= 2]
            players.append(dict(zip(contestheaders, cells)))

    return {'{}_{}_{}'.format(p.get('name'), p.get('position'), p.get('team')): p for p in players}
        
def ffnproj(scraper, week, pos):
    '''
    Gets positional projection from ffnerd
    
    Args:
        scraper: 
        week: 
        pos: 

    Returns:

    '''
    content = scraper.weekly_rankings(week=week, pos=pos)
    parser = FFNerdNFLParser()
    players = parser.weekly_rankings(content)
    logging.info(random.choice(players))
    return players

def fpranks(scraper, week, pos, fmt='ppr'):
    '''
    Parses fantasypros ranks for 1 week and 1 position
 
    Args:
        scraper:
        week:
        pos:
        fmt:
        
    Returns:
        list of dict
    '''
    parser = FantasyProsNFLParser()
    return parser.weekly_rankings(scraper.weekly_rankings(pos, fmt, week))
    

def xref(dkp, proj):
    '''
    Adds ffnerd projections to dk salaries
 
    Args:
        dkp: dict - of draftkings players
        proj: float - ffnerd projection

    Returns:
        
    '''
    for p in proj:
        key = '{}_{}'.format(p.get('name'), p.get('source_player_position'))
        if key in dkp:
            ppr_proj = p.get('ppr')
            if ppr_proj:
                dkp[key]['projection'] = float(p['ppr'])
            else:
                dkp[key]['projection'] = 0
    return dkp

def posdframe(dkp, pos):
    '''
    Creates pandas dataframe of qb, adds and removes columns
    
    Args:
        dkp: 

    Returns:

    '''
    vals = [v for k,v in dkp.items() if pos in k]
    df = pd.DataFrame([v for v in vals if 'projection' in v])
    pd.to_numeric(df.projection)

    # calculate max value
    max = df.projection.max()
    thresh = float(max/3)
    posdf = df.where(df['projection'] >= thresh).dropna()
    del posdf['game']
    del posdf['name_ID']
    posdf.salary = posdf.salary.apply(pd.to_numeric)
    posdf['salrank'] = posdf['salary'].rank(ascending=False)
    posdf['projrank'] = posdf['projection'].rank(ascending=False)
    posdf['diff'] = posdf.salrank - posdf.projrank
    return posdf

def ffn_dk():
    logging.basicConfig(level=logging.ERROR)
    contestfn = os.path.join(os.path.expanduser('~'), 'Downloads/DKEntries_w15.csv')
    savefn = os.path.join(os.path.expanduser('~'), 'dkranks.pkl')
    ffnscraper = FFNerdNFLScraper(api_key='8x3g9y245w6a')
    dkp = dkplayers(contestfn)
    dfs = []

    for pos in ['QB', 'RB', 'WR', 'TE']:
        logging.info('starting {}'.format(pos))
        proj = ffnproj(ffnscraper, 14, pos)
        dkp = xref(dkp, proj)
        dfs.append(posdframe(dkp, pos))

    df = pd.concat(dfs, ignore_index = True)
    logging.info(df.nlargest(25, 'diff'))
    df.to_pickle(savefn)

@functools.lru_cache()
def fpros_dk(contestfn, savefn):
    # first get players / salaries from dk
    dkp = dkplayers(contestfn)

    # next get fantasy pros flex ranks
    fpscraper = FantasyProsNFLScraper(cache_name='fpros')
    fpparser = FantasyProsNFLParser()
    content = fpscraper.weekly_rankings(pos='flex', fmt='ppr')
    fpros_ranks = fpparser.weekly_rankings(content, pos='flex')

    # add salaries to flex ranks
    to_remove = []
    for idx, p in enumerate(fpros_ranks):
        key = '{}_{}_{}'.format(p['source_player_name'], p['source_player_position'], p['source_player_team'])
        if dkp.get(key):
            fpros_ranks[idx]['salary'] = dkp[key]['salary']
        else:
            match, confidence = process.extractOne(key, list(dkp.keys()))
            if confidence >= 80:
                fpros_ranks[idx]['salary'] = dkp[match]['salary']
            else:
                logging.warning('no match for {} at {} -- {}'.format(key, confidence, match))
                to_remove.append(key)

    # only return players with salaries
    wanted = ['avg', 'salary', 'source_player_name', 'source_player_position', 'source_player_team']
    return [{k:v for k,v in p.items() if k in wanted} for p in fpros_ranks if p.get('salary')]

@click.command()
@click.option('--dkfn')
@click.option('--savefn', default=os.path.join(os.path.expanduser('~'), 'dkranks.pkl'))
def run(dkfn, savefn):
    df = pd.DataFrame(fpros_dk(dkfn, savefn))
    df.columns = ['rank', 'sal', 'name', 'pos', 'team']
    df = df[['name', 'pos', 'team', 'rank', 'sal']]
    df.sal = pd.to_numeric(df.sal)
    df['rank'] = pd.to_numeric(df['rank'])
    df['posrank'] = df.groupby("pos")["rank"].rank()
    df['salrank'] = df.groupby("pos")["sal"].rank(ascending=False)
    df['posval'] = 0 - (df['posrank'] - df['salrank'])
    df = df.sort_values(['pos', 'posval'], ascending=False)
    df.to_pickle(savefn)/';::::::::::::::::;;'


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    run()
