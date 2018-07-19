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
        self.rounds = opts['rounds']

    def __repr__(self):
        return "[{0: <2}] {1: <20}({2})".format(
            self.pos, self.name, self.proj)


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

    def __init__(self, roster_size=18, position_limits=(("QB", 1, 3),("RB", 5, 8),("WR", 5, 8),("TE", 2, 4))):
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
            variables.append(solver.IntVar(0, 1, player.name))

        # maximize proj
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

        # round constraints
        # idea is that constraint decreases from 18 to 1
        # as the draft progresses
        # that is, a player that you would draft in round 2 would
        # not be available in round 3
        # downside is that you don't draft players early but can adjust
        # for that by setting probability threshold lower
        for round in range(1, self.roster_size + 1):
            cap = self.roster_size + 1 - round
            round_cap = solver.Constraint(cap, cap)
            for i, player in enumerate(all_players):
                if round in player.rounds:
                    round_cap.SetCoefficient(variables[i], 1)

        # roster size constraint
        size_cap = solver.Constraint(self.roster_size, self.roster_size)
        for variable in variables:
            size_cap.SetCoefficient(variable, 1)


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