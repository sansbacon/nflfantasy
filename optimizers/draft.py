# nflfantasy.optimizers.dk
# provides optimization of DK lineup

import logging

from ortools.linear_solver import pywraplp


class Player(object):
    def __init__(self, opts):
        """
        Args:
            opts(dict):

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.id = opts['pid']
        self.name = opts['plyr']
        self.pos = opts['pos'].upper()
        self.team = opts['team'].upper()
        self.proj = float(opts['proj'])
        self.lock = int(opts.get('lock', 0)) > 0
        self.ban = int(opts.get('lock', 0)) < 0

    def __repr__(self):
        return "[{0: <2}] {1: <20}(${2}, {3}) {4}".format(
            self.pos, self.name, self.sal, self.proj, "LOCK" if self.lock else "")


class Roster(object):
    """

    """
    POSITION_ORDER = {
        "QB": 0,
        "RB": 1,
        "WR": 2,
        "TE": 3
    }

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.players = []

    def add_player(self, player):
        self.players.append(player)

    def proj(self):
        return sum(map(lambda x: x.proj, self.players))

    def position_order(self, player):
        return self.POSITION_ORDER[player.pos]

    def sorted_players(self):
        return sorted(self.players, key=self.position_order)

    def __repr__(self):
        s = '\n'.join(str(x) for x in self.sorted_players())
        s += "\n\nProjected Score: %s" % self.proj()
        return s


class NFLOptimizerDraftBestball(object):
    '''

    '''

    def __init__(self, roster_size=18, position_limits=(("QB", 1, 3),("RB", 5, 8),("WR", 5, 8),("TE", 2, 3))):
        '''
        NFLOptimizerDraftBestball object

        Args:
            roster_size(int): default 18
            position_limits(list): of list

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.roster_size = roster_size
        self.position_limits = position_limits

    def _optimize(self, all_players):
        '''
        Optimizes Draft bestball team

        Args:
            all_players(list): of Player

        Returns:
            Roster

        '''
        solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        variables = []

        # locks and bans
        # can use these to optimize when I've already made a few picks
        for player in all_players:
            if player.lock:
                variables.append(solver.IntVar(1, 1, player.name))
            elif player.ban:
                variables.append(solver.IntVar(0, 0, player.name))
            else:
                variables.append(solver.IntVar(0, 1, player.name))

        # maximize proj (surplus value)
        objective = solver.Objective()
        objective.SetMaximization()
        for i, player in enumerate(all_players):
            objective.SetCoefficient(variables[i], player.proj)

        # position limit constraints
        for position, min_limit, max_limit in self.position_limits:
            position_cap = solver.Constraint(min_limit, max_limit)
            for i, player in enumerate(all_players):
                if position == player.pos:
                    position_cap.SetCoefficient(variables[i], 1)

        # roster size constraint
        size_cap = solver.Constraint(self.roster_size, self.roster_size)
        for variable in variables:
            size_cap.SetCoefficient(variable, 1)

        # need to add constraint for rounds 1-18
        # not sure how to model this
        # may want to pick player with 16th round ADP in 13th round

        # need to add constraint can only choose player once
        #player_cap = solver.Constraint(0, 1)
        #for i, player in enumerate(all_players):
        #    position_cap.SetCoefficient(variables[i], 1)

        # if solve, then return Roster object
        # otherwise, return None
        roster = Roster()
        solution = solver.Solve()
        if solution == solver.OPTIMAL:
            for i, player in enumerate(all_players):
                if variables[i].solution_value() == 1:
                    roster.add_player(player)
        else:
            logging.error("No solution :(")
        return roster

    def optimize(self, all_players, n=1):
        '''
        Generator for multiple simulations

        Args:
            all_players(list): of Player
            n(int): number of Roster

        Returns:
            Roster

        '''
        for _ in range(n):
            roster = self._optimize(all_players)
            yield roster

if __name__ == '__main__':
    pass