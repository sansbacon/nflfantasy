#!/usr/bin/env bash

/usr/bin/python3.5 /home/sansbacon/workspace/nfl/scripts/fpros_weekly.py --fmt=std --weekstart=$1 --weekend=$2
/usr/bin/python3.5 /home/sansbacon/workspace/nfl/scripts/fpros_weekly.py --fmt=ppr --weekstart=$1 --weekend=$2
/usr/bin/python3.5 /home/sansbacon/workspace/nfl/scripts/fpros_weekly.py --fmt=hppr --weekstart=$1 --weekend=$2

