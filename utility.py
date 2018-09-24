# nflfantasy/utility.py
# various functions
from random import randint, random, shuffle, uniform


def _choice(seq):
    '''
    Use for numba compatibility - does not support choice or sample

    Returns:

    '''
    return seq[randint(0, len(seq) - 1)]


def _sample(ps, n):
    '''
    Use for numba compatibility - does not support choice or sample

    Returns:

    '''
    idx = range(0, len(ps))
    return [ps[x] for x in shuffle(idx)[0:n]]


def alter_projection(p, keys, projection_formula, randomize=False):

    if len(keys) != 3:
        raise ValueError('need keys for mean_projection, ceiling, and floor')

    mean_projection = p.get(keys[0], 0)
    ceiling = p.get(keys[1], 0)
    floor = p.get(keys[2], 0)

    if randomize:
        projections = [mean_projection + round(mean_projection * uniform(-.05, .05), 2)]
        ceilings = [ceiling + round(ceiling * uniform(-.05, .05), 3)]
        floors = [floor + round(floor * uniform(-.05, .05), 3)]
    else:
        projections = [mean_projection]
        ceilings = [ceiling]
        floors =[floor]

    if projection_formula == 'cash':
        try:
            proj = (_choice(projections) * .5) + (_choice(ceilings) * .15) + (_choice(floors) * .35)
        except:
            proj = _choice(projections)

    elif projection_formula == 'tournament':
        try:
            proj = (_choice(projections) * .3) + (_choice(ceilings) * .6) + (_choice(floors) * .1)
        except:
            proj = _choice(projections)

    elif projection_formula == 'tourncash':
        try:
            proj = (_choice(projections) * .4) + (_choice(ceilings) * .3) + (_choice(floors) * .3)
        except:
            proj = _choice(projections)

    elif ',' in projection_formula:
        try:
            avg, ceiling, floor = projection_formula.split(',')
            proj = (_choice(projections) * float(avg)) + (_choice(ceilings) * float(ceiling)) + (_choice(floors) * float(floor))
        except:
            proj = _choice(projections)

    else:
        proj = _choice(projections)

    return proj


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


if __name__ == '__main__':
    pass
