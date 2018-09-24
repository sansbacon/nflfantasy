# f4f-pydfs-pipeline.py
# creates pipeline from 4 for 4 projections to DK optimizer

"""
Examples:
    python ~/workspace/nfl_workflow/f4f-pydfs-pipeline.py \
      --season_year=2018 --week=3 \
      --source="dk" \
      --off_slate="NYJ|CLE|NE|DET|TB|PIT" \
      --n=5 \
      --dst_price=2200 \
      --randomize=True

"""

import logging
import os
from pathlib import Path
import sys

import click
import feather
import pandas as pd
from pydfs_lineup_optimizer import *

from nfl.utility import getdb
from nflfantasy.pipelines.f4f import *


@click.command()
@click.option('--season_year', type=int, help='Season')
@click.option('--week', type=int, help='Week')
@click.option('--source', type=str, help='dk, fd, yahoo, etc.')
@click.option('--dst_salary', default=0, type=int, help='salary to plug in for dummy DST')
@click.option('--off_slate', type=str, default=None, help='pipe-separated list of teams not on slate')
@click.option('--missing_sals', type=str, default=None, help='pipe-separated list of missing salaries')
@click.option('--dbname', default='nfl', type=str, help='Database name')
@click.option('--n', default=5, type=int, help='number of lineups')
@click.option('--randomize', default=False, type=bool, help='Randomly adjust projections')
@click.option('--verbose', default=True, type=bool, help='Show log on stdout')
def run(season_year, week, source, dst_salary, off_slate, missing_sals, 
        dbname, n, randomize, verbose):
    '''
    Parses 4 for 4 projections then runs optimizer
    
    Args:
        season_year(int): NFL season
        week(int): NFL week
        source(str): dfs site (dk, fd, yahoo, etc.)
        dst_salary(int): default salary for dummy DST
        off_slate(str): pipe-delimited team codes, default None
        missing_sals(str): pipe-delimited salaries, default None
        dbname(str): database name, default 'nfl'
        n(int): number of lineups, default 5
        randomize(bool): jitter projections, default False
        verbose(bool): show logging output on stdout, default True
        
    Returns:
        None
        
    '''
    # setup
    db = getdb(dbname)

    # test if already have projections - no need to update otherwise
    # projdir = projections directory
    # projf = filename for projections feather file
    # frfn = full path of R script
    projdir = Path(os.path.dirname(os.path.realpath(__file__))) / 'projections'    
    projfthr_clean = projdir / '4for4' / '{}_w{}_f4f-{}proj_clean.feather'.format(season_year, week, source)
    projcsv = projdir / '4for4' / '{}_w{}_f4f-{}proj.csv'.format(season_year, week, source)
    
    # load datafile - is csv the first time around
    if projfthr_clean.is_file():
        df = feather.read_dataframe(str(projfthr_clean))
    else:
        # clean: column_names, relevant columns, team names
        # remove off slate
        # filter players by threshold
        # match salaries
        # add dummy DST
        # save results so don't need to match again
        df = pd.read_csv(str(projcsv))
        df = clean_df(df)
        off_slate = off_slate.split('|')
        if off_slate:
            df = df.query('team not in @off_slate')
        df = filter_players(df)
        df = add_salaries(df, db, source, season_year, week)
        if dst_salary:
            df = add_dst(df, dst_salary)
        feather.write_dataframe(df, str(projfthr_clean))
     
    # run optimizer
    lineups = []
    players = df_to_players(df)
    o = optimizer_factory(source, players)
    if randomize:
        dev = o.set_deviation(0.05, 0.2)
        for i in range(n):
            l = next(o.optimize(1, randomness=True))
            lineups.append(l)
    else:
        for l in o.optimize(n):
            lineups.append(l)
    df, summdf = lineups_to_df(lineups, 'opt.feather')
    print(summdf)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    run()
