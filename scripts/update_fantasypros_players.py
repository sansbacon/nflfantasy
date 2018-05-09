import logging

import requests
from fuzzywuzzy import process

from nfl.player.playerxref import *
from nfl.utility import getdb

db = getdb()

# step one: direct match -- nfl and fantasypros
## nflcom players: dict, key is name, value is list of players
nflp = nflcom_players(db)
nflpkeys = list(nflp.keys())

## fantasypros players
r = requests.get('https://www.fantasypros.com/ajax/player-search.php') 
fppl = r.json() 
unmatched_d = {}
error_d = {}
n = len(fppl)

for idx, fp in enumerate(fppl):
    # skip if already have nflcom_player_id
    if fp.get('nflcom_player_id'):
        continue
    
    # skip if already in unmatched
    if fp.get('name') and fp.get('position'):
        key = '{}_{}'.format(fp['name'], fp['position'])
        if key in unmatched_d:
            continue
    else:
        print('could not get {}'.format(fp))
        
    # otherwise build up dict
    try:
        p = {'source': 'fantasypros'}
        p['source_player_name'] = fp['name']
        p['source_player_code'] = fp['filename'].split('.php')[0]
        p['source_player_id'] = fp['id']
        p['source_player_position'] = fp['position']
    except:
        print('error with {}'.format(fp))
        continue

    ## attempt direct match 
    ## if direct match, then add nflcom_player_id
    ## if no direct match, then try fuzzy match
    match = nflp.get(key)
    if match:
        if len(match) == 1: 
            p['nflcom_player_id'] = match[0]['player_id']
            fppl[idx] = p
            continue
    else:
        match, confidence = process.extractOne(key, nflpkeys)  
                       
        # most misses have same name and pos vs. UNK from nfldb
        # can solve that without doing fuzzy match
        nm, ps = match.split('_')
        if nm == p['source_player_name'] and ps == 'UNK':
            nflplyr = nflp[match]
            if len(nflplyr) == 1:
                p['nflcom_player_id'] = nflplyr[0]['player_id']
                fppl[idx] = p
                continue
        elif confidence >= 92:
            nflplyr = nflp[match]
            if len(nflplyr) == 1:
                p['nflcom_player_id'] = nflplyr[0]['player_id']
                fppl[idx] = p
                continue       
        elif confidence >= 75:
            print('{}/{}: {} | {} | {}'.format(idx, n, key, match, confidence))
            is_match = input("Is this a match? ")
            if is_match == 'y':
                nflplyr = nflp[match]
                if len(nflplyr) == 1:
                    p['nflcom_player_id'] = nflplyr[0]['player_id']
                    fppl[idx] = p
                    continue
            # can log mistake from last item    
            elif is_match == 'e':
                try:
                    key = '{}_{}'.format(fppl[idx-1]['name'], fppl[idx-1]['position'])
                    error_d[key] = fppl[idx-1]
                except:
                    try:
                        key = '{}_{}'.format(fppl[idx-1]['source_player_name'], 
                                      fppl[idx-1]['source_player_position'])
                        error_d[key] = fppl[idx-1]
                    except:
                        pass
    unmatched_d[key] = p
    
    
player_pos = {
'DE,EDR': 'DE',
'DT,DE': 'DL',
'LB,DE': 'OLB',
'S': 'SAF',
}

manual = []
for k in list(unmatched_d.keys()):
    match = nflp.get(k)
    if match:
        unmatched_d[k]['nflcom_player_id'] = match['player_id']
    else:
        for match, confidence in process.extract(k, nflpkeys, limit=5):
            print('{} | {} | {}'.format(k, match, confidence))
            is_match = input("Is this a match? ")
            if is_match == 'y':
                nflplyr = nflp[match]
                if len(nflplyr) == 1:
                    unmatched_d[k]['nflcom_player_id'] = nflplyr[0]['player_id']
                    continue
        manual.append(unmatched_d.pop(k))