# pipelines/fb.py
# pipelines for fanball.com

import logging

import feather
import pandas as pd

import nfl.xref as nx


logging.getLogger(__name__).addHandler(logging.NullHandler())


def get_fb_salary(r, mfld, sald, interactive=False, defaultsal=2000):
    '''
    Adds salary based on player match

    Args:
        r(DataFrame): DataFrame row
        mfld(dict): dict of mfl_id: fb_player_id
        sald(dict): dict of fb_player_id: salary
        interactive(bool): do interactive matching, default False
        defaultsal(int): supply salary if no match, default 2000

    Returns:
        int

    '''
    # if already have salary, can skip
    ## otherwise add salaries
    if r['salary'] > 0:
        sal = r['salary']
    elif mfld.get(r['id']):
        fb_player_id = mfld.get(r['id'])
        sal = sald.get(fb_player_id, defaultsal)
    elif interactive:
        sal = input('Enter salary for {}: '.format(p['full_name']))
    else:
        sal = defaultsal
    return int(sal)


def fb_salary_dict(db, season_year, week):
    '''
    Returns dict of id:salary
    
    Args:
        season_year(int):
        week(int):
        
    Returns:
        dict
        
    '''
    q = """SELECT source_player_id as id, salary as s
           FROM dfs.fbsal 
           WHERE season_year={} AND week={};"""
    return {p['id']: p['s'] for p in 
              db.select_dict(q.format(season_year, week))}
    
    
if __name__ == '__main__':
    pass
