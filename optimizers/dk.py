# nflfantasy.optimizers.dk
# provides optimization of DK lineup

from collections import defaultdict
import logging

from ortools.linear_solver import pywraplp


class Player(object):
    def __init__(self, opts):
        """
        Args:
            opts(dict):

        """
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.id = str(opts['pid'])
        self.name = opts['plyr']
        self.pos = opts['pos'].upper()
        self.team = opts['team'].upper()
        self.sal = int(opts['sal'])
        self.proj = float(opts['proj'])
        self.lock = int(opts.get('lock', 0)) > 0
        self.ban = int(opts.get('lock', 0)) < 0
        if opts.get('posrk'):
            self.posrk = float(opts['posrk'])
        if opts.get('salrk'):
            self.salrk = float(opts['salrk'])

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

    def __init__(self, dst_cost=3000):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.players = []
        self.dst_cost = dst_cost

    def add_player(self, player):
        self.players.append(player)

    def spent(self):
        return sum(map(lambda x: x.sal, self.players)) + self.dst_cost

    def proj(self):
        return sum(map(lambda x: x.proj, self.players))

    def position_order(self, player):
        return self.POSITION_ORDER[player.pos]

    def sorted_players(self):
        return sorted(self.players, key=self.position_order)

    def __repr__(self):
        s = '\n'.join(str(x) for x in self.sorted_players())
        s += "\n\nProjected Score: %s" % self.proj()
        s += "\tCost: $%s" % self.spent()
        return s


class NFLOptimizerDK(object):
    '''

    '''

    def __init__(self, dst_cost=3000, roster_size=8, salary_cap=47000,
                 position_limits=[["QB", 1, 1],["RB", 2, 3],["WR", 3, 4],["TE", 1, 2]]):
        '''
        NFLOptimizerDK object

        Args:
            dst_cost(int): default 3000
            roster_size(int): default 8
            salary_cap(int): default 47000
            position_limits(list): of list

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.dst_cost = dst_cost
        self.roster_size = roster_size
        self.salary_cap = salary_cap
        self.position_limits = position_limits

    def _optimize(self, all_players, max_score, solver_name):
        '''
        Optimizes draftkings NFL team

        Args:
            all_players(list): of Player
            max_score(float): constraint
            solve_name(str): e.g. 'Gurobi'

        Returns:
            roster(Roster)
            solver(pywraplp.Solver)
            variables(list):

        '''
        if solver_name.lower() == 'gurobi':
            try:
                solver = pywraplp.Solver('FD', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)
            except:
                logging.error('could not use Gurobi')
                solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        else:
            solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        variables = []

        # locks and bans
        for player in all_players:
            if player.lock:
                variables.append(solver.IntVar(1, 1, player.id))
            elif player.ban:
                variables.append(solver.IntVar(0, 0, player.id))
            else:
                variables.append(solver.IntVar(0, 1, player.id))

        # maximize proj (fantasy points)
        objective = solver.Objective()
        objective.SetMaximization()
        for i, player in enumerate(all_players):
            objective.SetCoefficient(variables[i], player.proj)

        # salary cap constraint
        sal_cap = solver.Constraint(0, self.salary_cap)
        for i, player in enumerate(all_players):
            sal_cap.SetCoefficient(variables[i], player.sal)

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

        # score cap constraint (useful if generating multiple lineups)
        # can generate multiple lineups if have cap on lineup score
        if max_score:
            score_cap = solver.Constraint(0, max_score)
            for i, player in enumerate(all_players):
                score_cap.SetCoefficient(variables[i], player.proj)

        # if solve, then return Roster object
        # otherwise, return None
        roster = Roster(dst_cost=self.dst_cost)
        solution = solver.Solve()
        if solution == solver.OPTIMAL:
            for i, player in enumerate(all_players):
                if variables[i].solution_value() == 1:
                    roster.add_player(player)
        else:
            logging.error("No solution :(")
        return roster, solver, variables

    def _optimize_diverse(self, all_players, existing_lineups, solver_name,
                          overlap=5, player_cap=50):
        '''
        Optimizes draftkings NFL team with diverse lineup constraints

        Args:
            all_players(list): of Player
            existing_lineups(list): of list of Player
            solve_name(str): e.g. gurobi
            overlap(int): how many players can overlap, default 6

        Returns:
            Roster

        '''
        if solver_name.lower() == 'gurobi':
            try:
                solver = pywraplp.Solver('FD', pywraplp.Solver.GUROBI_MIXED_INTEGER_PROGRAMMING)
            except:
                logging.error('could not use Gurobi')
                solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
            else:
                solver = pywraplp.Solver('FD', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)

        variables = []

        # locks and bans
        for player in all_players:
            if player.lock:
                variables.append(solver.IntVar(1, 1, player.id))
            elif player.ban:
                variables.append(solver.IntVar(0, 0, player.id))
            else:
                variables.append(solver.IntVar(0, 1, player.id))

        # maximize proj (fantasy points)
        objective = solver.Objective()
        objective.SetMaximization()
        for i, player in enumerate(all_players):
            objective.SetCoefficient(variables[i], player.proj)

        # salary cap constraint
        sal_cap = solver.Constraint(0, self.salary_cap)
        for i, player in enumerate(all_players):
            sal_cap.SetCoefficient(variables[i], player.sal)

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

        # diversity cap constraint (useful if generating multiple lineups)
        # can generate multiple lineups that don't overlap too much
        for lineup in existing_lineups:
            diversity_cap = solver.Constraint(0, overlap)
            for player in lineup.sorted_players():
                # lookup index of player in all_players
                # then set coefficient of that index to 1
                i = [i for i, p in enumerate(all_players) if p.id == player.id][0]
                logging.info('added {} to diversity cap'.format(player.id))
                diversity_cap.SetCoefficient(variables[i], 1)
            logging.info(diversity_cap)

        # player cap constraint
        player_cap = solver.Constraint(0, player_cap)
        players = defaultdict(int)
        for lineup in existing_lineups:
            for player in lineup.players:
                players[player.id] += 1
        for pid, val in players.items():
            i = [i for i, p in enumerate(all_players) if p.id == pid][0]
            player_cap.SetCoefficient(variables[i], val)

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

    def optimize(self, all_players, n=5, max_score=500.0, solver_name='gurobi'):
        '''
        Generator for multiple simulations

        Args:
            all_players(list): of Player
            n(int): number of Roster
            max_score(float): upper constraint

        Returns:
            Roster

        '''
        for _ in range(n):
            roster = self._optimize(all_players, max_score=max_score, solver_name=solver_name)
            max_score = roster.proj() - .01
            yield roster

    def optimize_diverse(self, all_players, n=5, solver_name='gurobi',
                         overlap=5, player_cap=50):
        '''
        Generator for multiple simulations

        Args:
            all_players(list): of Player
            n(int): number of Roster
            solver_name(str): 'gurobi', 'cbc', etc.
        Returns:
            Roster

        '''

        # seed the process by getting the optimal lineup
        roster, solver, variables = self._optimize(all_players=all_players, max_score=None, solver_name=solver_name)

        # now go through and reuse the solver + constraints
        # then only need to add newest lineup to the mix
        for i in range(n - 1):
            roster, solver = self._optimize_diverse(solver, roster, variables)
            max_score = roster.proj() - .01
            yield roster

    def optimize_stack(self, all_players):
        '''
        Tests whether stacking is more effective than not stacking
        Compare optimal lineup with QB vs. QB stacked with 1 WR
        So should be 4 optimal lineups per team per week

        Args:
            all_players(list): of Player

        '''
        stacks = defaultdict(list)

        # go through each team
        # team is the key for stacks, value is list of Roster
        for team in sorted(set([p.team for p in all_players])):
            logging.info('starting {}'.format(team))
            # get the indices of the qbs on this team
            qbidx = [i for i, p in enumerate(all_players)
                     if p.pos == 'QB' and p.team == team]

            # if there's a qb, then lock him in alone and run sim
            if qbidx:
                # skip unless top-20 qb:
                if all_players[qbidx[0]].posrk > 20:
                    continue

                logging.info('starting {}'.format(all_players[qbidx[0]].name))
                all_players[qbidx[0]].lock = 1
                lineup = self._optimize(all_players)
                stacks[team].append(lineup)

                # now try stacks of qb + WR1, WR2, WR3
                # have to make sure to remove the locks for each WR
                wridx = [i for i, p in enumerate(all_players)
                         if p.pos == 'WR' and p.team == team]
                for idx in wridx[0:3]:
                    logging.info('starting {}, {}'.format(
                    all_players[qbidx[0]].name,
                    all_players[idx].name))
                    all_players[idx].lock = 1
                    lineup = self._optimize(all_players)
                    stacks[team].append(lineup)
                    all_players[idx].lock = 0

                    # remove QB lock and move to new team
                    all_players[qbidx[0]].lock = 0
        return stacks


if __name__ == '__main__':
    pass