def draft_order(rounds, participants):
    '''
    List of picks for snake draft
    
    Args:
        rounds(int): # of rounds in draft
        participants(int): # of teams
    
    Returns:
        list: of int
        
    '''
    picks = []
    for round in range(1, rounds + 1):
        if round % 2 == 1:
            picks += range(1, participants + 1)
        else:
            picks += reversed(range(1, participants + 1))
    return picks
