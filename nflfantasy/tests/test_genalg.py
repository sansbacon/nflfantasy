import logging
import pickle
from random import sample
import unittest

from nfl.optimizers.genalg import GenAlg


class TestGenalg(unittest.TestCase):

    def setUp(self):
        self.ga = GenAlg()
        self.pop = []
        with open('data/genalg-players.pkl') as infile:
            players = pickle.load(infile)
        names = {}
        for p in players:
            n = p.get('Player_Name')
            if names.get(n):
                continue
            else:
                names[n] = p
        self.ga.players = self.ga.load_players(players=names.values(), projection_formula='tourncash')
        self.pop = self.ga.CreatePopulation(1000)

    def test_instantiate(self):
        self.assertIsInstance(self.ga, GenAlg)

    def test_CreatePopluation(self):
        self.pop = self.ga.CreatePopulation(1000)
        self.assertIsInstance(self.pop, list)

    def test_Breed(self):
        self.pop = self.ga.CreatePopulation(1000)
        parents = sample(self.pop, 2)
        for idx,t in enumerate(self.ga.breed(*parents)):
            self.ga.printTeam(parents[idx])
            self.ga.printTeam(t)

    def test_Mutate(self):
        self.pop = self.ga.CreatePopulation(1000)
        t = sample(self.pop, 1)
        self.ga.printTeam(*t)
        print '\n'
        self.ga.printTeam(self.ga.mutate(*t))

    def test_Evolve(self):
        self.pop = self.ga.CreatePopulation(1000)
        nextgen = self.ga.evolve(self.pop)
        for i in range(1,10):
            nextgen = self.ga.evolve(nextgen)
            print sum([self.ga.GetTeamPointTotal(t) for t in nextgen]) / float(len(nextgen))

    def test_run_solver(self):
        teams = self.ga.run_solver(self.ga.players, pop_size=10000)
        best = [teams.pop(0)]
        counter = 0
        max = 20
        for t in teams:
            if self.ga.GetTeamPointTotal(t) < self.ga.GetTeamPointTotal(best[-1]):
                if counter <= max:
                    print self.ga.GetTeamPointTotal(best[-1])
                    best.append(t)
                    print 'added team, counter is {}'.format(counter)
                    counter += 1
                    print 'counter incremented to {}'.format(counter)
                else:
                    break


if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG)
    #unittest.main()
    pass