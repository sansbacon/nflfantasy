## draft-player-ownership.py
## idea is to get my ownership rates on players
## hard to scrape site, so process manually collected info

import json
import pandas as pd
from nfl.utility import merge_two

# helper functions
def _bookings_convertk(k):
    '''
    Converts keys in dict
    
    Args:
        k (str): dictionary key
        
    Returns:
        str: new dictionary key
    '''
    _convertd = {'id': 'booking_id'}
    if _convertd.get(k):
        return _convertd.get(k)
    else:
        return k


def _process_players(bookings, players):
    '''
    Merges information from DRAFT.com bookings and players
    
    Args:
        bookings (list): of dict
        players (list): of dict
        
    Returns:
        list: of dict
        
    '''
    merged = []
    
    # go through bookings first
    # create bookings dict with player_id: player_dict
    b_wanted = ['id', 'player_id', 'position_id', 'projected_points']
    bd = {b['player_id']: {_bookings_convertk(k):v for k,v in b.items() if k in b_wanted}
          for b in bookings}
    
    # now try to match up with players
    p_wanted = ['first_name', 'last_name', 'team_id', 'injury_status']
    for p in players:
        match = bd.get(p['id'])
        if match:
            merged.append(merge_two(match, {k:v for k,v in p.items()
                                            if k in p_wanted}))
    return merged
    
    
def _process_positions(positions):
    '''
    Gets DRAFT.com id and name for NFL positions
    
    Args:
        positions (list): of dict
        
    Returns:
        dict
        
    '''
    return {int(pos['id']): pos['name'] for pos in positions}


def _process_teams(teams):
    '''
    Gets DRAFT.com id and abbreviation for NFL teams
    
    Args:
        teams (list): of dict
        
    Returns:
        dict
        
    '''
    return {team['id']: team['abbr'] for team in teams}


def _process_users(users):
    '''
    Gets useful information from DRAFT.com users dict
    
    Args:
        users (list): of dict
        
    Returns:
        list: of dict
        
    '''
    wanted = ['id', 'username', 'experienced', 'skill_level']
    return [{k:v for k,v in user.items() if k in wanted}
             for user in users]

def _entry_fee(payouts):
    '''
    Determines entry fee from payouts
    
    Args:
        payouts(list): of dict
    
    Returns:
        int
        
    '''
    payout = payouts[0]
    if payout['cash'] == '4.5':
        return 1
    elif payout['cash'] == '13.5':
        return 3
    else:
        return None
    
    
# process a single draft
def process_draft(draft):
    '''
    Processes a single DRAFT.com draft
    
    Args:
        draft(dict): dict representing single draft

    Returns:
        dict: 
        
    '''
    positions = _process_positions(draft['positions'])
    users = _process_users(draft['users'])
    teams = _process_teams(draft['teams'])
    players = _process_players(draft['bookings'], 
                draft['players'])
    players_d = {p['booking_id']: p for p in players}
    users_d = {u['id']: u['username'] for u in users}
    
    # now go through rosters
    # for each roster, loop through picks
    picks = []
    entry_fee = _entry_fee(draft['payouts'])
    for roster in draft['draft_rosters']:
        pick_wanted = ['id', 'draft_roster_id', 'points', 'auto_picked',
                       'pick_number', 'slot_id', 'booking_id']                      
        for pick in roster['picks']:
            pk = {k:v for k,v in pick.items() if k in pick_wanted}
            pk['draft_id'] = draft['id']
            pk['draft_time'] = draft['start_time']
            pk['draft_size'] = draft['max_participants']
            pk['entry_fee'] = entry_fee
            pk['pick_order'] = roster['pick_order']
            pk['user_id'] = roster['user_id']
            pk['user_name'] = users_d[pk['user_id']]
            pk = merge_two(pk, players_d[pk['booking_id']])
            pk['team_name'] = teams.get(pk.get('team_id', ''))
            pk['position'] = positions.get(pk.get('position_id', ''))
            picks.append(pk)
            
    return positions, users, teams, players, picks
    
def run():
    # list of draft dictionaries from various drafts
    all_picks = []
    with open('draft-drafts.json', 'r') as f:            
        for draft in json.load(f):
            pos, u, t, p, pks = process_draft(draft['draft'])
            all_picks += pks

    df = pd.DataFrame(all_picks)
    wanted = ['draft_id', 'entry_fee', 'user_name', 'player_id', 'first_name', 
              'last_name', 'team_name', 'position', 'pick_number']
    
    
if __name__ == '__main__':
    run()
