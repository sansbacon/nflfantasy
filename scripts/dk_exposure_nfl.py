'''
dk_exposure_nfl.py
prints sorted list of player exposure by contest

arguments:
    --fn

usage:
    python dk_exposure_nfl.py --fn=/home/nfldb/DKEntries.csv
'''

from collections import defaultdict
import logging
import pprint
import sys

import click

from nba.parsers.draftkings import DraftKingsNBAParser


@click.command()
@click.option('--fn')
def run(fn):
    dkparser = DraftKingsNBAParser()
    exposure = defaultdict(lambda: defaultdict(int))
    positions = ['QB', 'RB1', 'RB2', 'WR1', 'WR2', 'WR3', 
                 'TE', 'FLEX', 'DST']

    for entry in dkparser.slate_entries(fn):
        contest = entry.get('Contest Name')
        for pos in positions:
            name = entry[pos].replace(' (LOCKED)', '')
            exposure[contest][name] += 1

    for k,v in exposure.items():
        pprint.pprint(sorted(v.items(), key=lambda x: (x[1],x[0]), reverse=True))


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    run()
