import logging
from operator import add
from random import choice, randint, random, sample, shuffle, uniform

class Player(object):
    def __init__(self, name, team, oppos, position, salary, projection):
        self.self = self
        self.name = name
        self.team = team
        self.opp = oppos
        self.position = position
        self.salary = salary
        self.points = projection

    def __iter__(self):
        return iter(self.list)

    def __str__(self):
        return "{} {} {} {}".format(self.name ,self.position ,self.salary, self.points)


class GenAlg(object):

    def __init__(self, players=[], pool={}, positions=['qb', 'rb', 'wr', 'te', 'flex', 'dst']):
        self.players = players
        self.pool = pool
        self.positions = positions
        self._qbs = []
        self._rbs = []
        self._wrs = []
        self._tes = []
        self._dsts = []
        self._flexs = []

    @property
    def qbs(self):
        if not self._qbs:
            self._qbs = [player for player in self.players if player.position == 'QB' and player.points >= 16]
        return self._qbs

    @property
    def rbs(self):
        if not self._rbs:
            self._rbs = [player for player in self.players if player.position == 'RB' and player.points >= 9]
        return self._rbs

    @property
    def wrs(self):
        if not self._wrs:
            self._wrs = [player for player in self.players if player.position == 'WR' and player.points >=9]
        return self._wrs

    @property
    def tes(self):
        if not self._tes:
            self._tes = [player for player in self.players if player.position == 'TE' and player.points >= 7]
        return self._tes

    @property
    def dsts(self):
        if not self._dsts:
            self._dsts = [player for player in self.players if player.position == 'DST' and player.points >= 6]
        return self._dsts

    @property
    def flexs(self):
        if not self._flexs:
            self._flexs = [player for player in self.players if player.position != 'QB' and player.position != 'DST' and player.points >= 8]
        return self._flexs

    def CreatePopulation(self, count):
        return [self.CreateRandomTeam() for i in range(0, count)]

    def getPlayers(self, pos, n):
        '''
        Use for numba compatibility - does not support choice or sample
        Args:
            pos(str): QB, RB, WR, TE, DST
            n(int): how many of the position needed

        Returns:

        '''
        if pos == 'QB':
            idx = range(0,len(self.qbs))
            ps = [self.qbs[x] for x in shuffle(idx)[0:n]]

        elif pos == 'RB':
            idx = range(0,len(self.rbs))
            ps = [self.rbs[x] for x in shuffle(idx)[0:n]]

        elif pos == 'WR':
            idx = range(0,len(self.wrs))
            ps = [self.wrs[x] for x in shuffle(idx)[0:n]]

        elif pos == 'TE':
            idx = range(0,len(self.tes))
            ps = [self.tes[x] for x in shuffle(idx)[0:n]]

        elif pos == 'FLEX':
            idx = range(0,len(self.flexs))
            ps = [self.flexs[x] for x in shuffle(idx)[0:n]]

        elif pos == 'DST':
            idx = range(0,len(self.dsts))
            ps = [self.dsts[x] for x in shuffle(idx)[0:n]]

        return ps

    def CreateRandomTeam(self):
        team = {
            'qb': sample(self.qbs, 1),
            'rb': sample(self.rbs, 2),
            'wr': sample(self.wrs, 3),
            'te': sample(self.tes, 1),
            'flex': sample(self.flexs, 1),
            'dst': sample(self.dsts, 1)
        }

        while True:
            flexer = team['flex'][0]
            if flexer in team['rb'] or flexer in team['wr'] or flexer in team['te']:
                team['flex'] = sample(self.flexs, 1)
            else:
                break

        return team

    def GetTeamPointTotal(self, team):
        total_points = 0
        for pos, players in team.items():
            for player in players:
                total_points += player.points
        return total_points

    def GetTeamSalary(self, team):
        total_salary = 0
        for pos, players in team.items():
            for player in players:
                total_salary += player.salary
        return total_salary

    def printTeam(self, team):
        print team['qb'][0]
        print team['rb'][0]
        print team['rb'][1]
        print team['wr'][0]
        print team['wr'][1]
        print team['wr'][2]
        print team['te'][0]
        print team['flex'][0]
        print team['dst'][0]
        print '${}, {} points'.format(self.GetTeamSalary(team), self.GetTeamPointTotal(team))

    def load_players(self, players, projection_formula=None, team_exclude=[], player_exclude=[], randomize_projections=True):
        '''
        Takes list of player dicts, returns list of Player objects
        :param players(list): of player dict
        :return: all_players(list): of Player
        '''
        all_players = []

        for p in players:
            oppos = str(p.get('Opposing_TeamFB', '').replace('@', ''))
            pos = str(p.get('Position'))
            if pos == 'D':
                pos = str('DST')
            team = str(p.get('Team'))
            player_name = str(p.get('Player_Name'))

            mean_projection = p.get('AvgPts', 0)
            ceiling = p.get('Ceiling', 0)
            floor = p.get('Floor', 0)

            if randomize_projections:
                projections = [mean_projection + round(mean_projection * uniform(-.05,.05), 2)]
                ceilings = [ceiling + round(ceiling * uniform(-.05,.05), 3)]
                floors = [floor + round(floor * uniform(-.05,.05), 3)]
            else:
                projections = [mean_projection]
                ceilings = [ceiling]
                floors = [floor]

            if projection_formula == 'cash':
                proj = (choice(projections) * .5) + (choice(ceilings) * .15) + (choice(floors) * .35)
            elif projection_formula == 'tournament':
                proj = (choice(projections) * .3) + (choice(ceilings) * .6) + (choice(floors) * .1)
            elif projection_formula == 'tourncash':
                proj = (choice(projections) * .4) + (choice(ceilings) * .3) + (choice(floors) * .3)
            elif ',' in projection_formula:
                avg, ceiling, floor = projection_formula.split(',')
                proj = (choice(projections) * avg) + (choice(ceilings) * ceiling) + (choice(floors) * floor)
            else:
                proj = choice(projections)

            if team in team_exclude:
                continue
            elif player_name in player_exclude:
                continue
            else:
                all_players.append(Player(projection=proj, position=pos, name=player_name, salary=p.get('Salary'), team=team, oppos=oppos))

        return all_players

    def fitness(self, team):
        points = self.GetTeamPointTotal(team)
        salary = self.GetTeamSalary(team)
        values = team.values()
        if salary > 50000:
            return 0
        return points

    def grade(self, pop):
        'Find average fitness for a population.'
        summed = reduce(add, (self.fitness(team) for team in pop))
        return summed / (len(pop) * 1.0)

    def listToTeam(self, players):
        return {
            'qb': [players[0]],
            'rb': players[1:3],
            'wr': players[3:6],
            'te': [players[6]],
            'flex': [players[7]],
            'dst': [players[8]]
        }

    def breed(self, mother, father):
        positions = ['qb', 'rb', 'wr', 'te', 'flex', 'dst']

        mother_lists = [mother['qb'] + mother['rb'] + mother['wr'] + mother['te'] + mother['flex'] + mother['dst']]
        mother_list = [item for sublist in mother_lists for item in sublist]
        father_lists = [father['qb'] + father['rb'] + father['wr'] + father['te'] + father['flex'] + father['dst']]
        father_list = [item for sublist in father_lists for item in sublist]

        index = choice([1, 3, 6, 7, 8])
        child1 = self.listToTeam(mother_list[0:index] + father_list[index:])
        child2 = self.listToTeam(father_list[0:index] + mother_list[index:])

        while True:
            flexer = child1['flex'][0]
            if flexer in child1['rb'] or flexer in child1['wr'] or flexer in child1['te']:
                child1['flex'] = sample(self.flexs, 1)
            else:
                break

        while True:
            flexer = child2['flex'][0]
            if flexer in child2['rb'] or flexer in child2['wr'] or flexer in child2['te']:
                child2['flex'] = sample(self.flexs, 1)
            else:
                break

        return [child1, child2]

    def mutate(self, team):

        random_pos = choice(self.positions)
        if random_pos == 'qb':
            team['qb'][0] = choice(self.qbs)
        if random_pos == 'rb':
            team['rb'] = sample(self.rbs, 2)
        if random_pos == 'wr':
            team['wr'] = sample(self.wrs, 3)
        if random_pos == 'te':
            team['te'][0] = choice(self.tes)
        if random_pos == 'flex':
            team['flex'][0] = choice(self.flexs)
        if random_pos == 'dst':
            team['dst'][0] = choice(self.dsts)

        while True:
            flexer = team['flex'][0]
            if flexer in team['rb'] or flexer in team['wr'] or flexer in team['te']:
                team['flex'] = sample(self.flexs, 1)
            else:
                break
        return team

    def evolve(self, pop, retain=0.35, random_select=0.05, mutate_chance=0.005):
        graded = [ (self.fitness(team), team) for team in pop]
        graded = [ x[1] for x in sorted(graded, reverse=True)]
        retain_length = int(len(graded)*retain)
        parents = graded[:retain_length]

        # randomly add other individuals to promote genetic diversity
        for individual in graded[retain_length:]:
            if random_select > random():
                parents.append(individual)

        # mutate some individuals
        for individual in parents:
            if mutate_chance > random():
                individual = self.mutate(individual)

        # crossover parents to create children
        parents_length = len(parents)
        desired_length = len(pop) - parents_length
        children = []
        while len(children) < desired_length:
            male = randint(0, parents_length-1)
            female = randint(0, parents_length-1)
            if male != female:
                male = parents[male]
                female = parents[female]
                babies = self.breed(male,female)
                for baby in babies:
                    children.append(baby)
        parents.extend(children)
        return parents

    def run_solver(self, players, pop_size=10000, n=None):
        best_teams = []
        history = []
        p = self.CreatePopulation(pop_size)
        fitness_history = [self.grade(p)]
        for i in xrange(40):
            p = self.evolve(p)
            fitness_history.append(self.grade(p))
            valid_teams = [team for team in p if self.GetTeamSalary(team) <= 50000]
            valid_teams = sorted(valid_teams, key=self.GetTeamPointTotal, reverse=True)
            if len(valid_teams) > 0:
                best_teams.append(valid_teams[0])
        for datum in fitness_history:
            history.append(datum)

        best_teams = sorted(best_teams, key=self.GetTeamPointTotal, reverse=True)

        if n:
            best_teams = best_teams[0:n]

        return best_teams

if __name__ == '__main__':
    pass