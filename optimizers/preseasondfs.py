import logging
import random

from collections import OrderedDict

class Lineup(object):

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.qb = None
        self.rb = []
        self.wr = []
        self.te = None
        self.flex = None
        self.dst = None
        d = OrderedDict()
        d['QB'] = 1
        d['RB'] = 2
        d['WR'] = 3
        d['TE'] = 1
        d['FLEX'] = 1
        d['DST'] = 1
        self.positions = d

    def __repr__(self):
        return 'Lineup(qb={}, rb={}, wr={}, te={}, flex={}, dst={})'.format(
                self.qb, ', '.join(self.rb), ', '.join(self.wr), self.te, self.flex, self.dst)

    def add(self, player):
        if player.get('pos') == 'QB':
            self.qb = player
        elif player.get('pos') == 'WR':
            if len(self.wr) < self.positions.get('WR'):
                self.wr.append(player)
            elif not self.flex:
                self.flex = player
            else:
                logging.error('wr and flex full: {}'.format(player))
        elif player.get('pos') == 'RB':
            if len(self.rb) < self.positions.get('RB'):
                self.rb.append(player)
            elif not self.flex:
                self.flex = player
            else:
                logging.error('rb and flex full: {}'.format(player))
        elif player.get('pos') == 'TE':
            self.te = player
        elif player.get('pos') == 'DST':
            self.dst = player
        elif player.get('pos') == 'FLEX':
            self.flex = player
        else:
            raise ValueError('position does not exist: {}'
                              .format(player.get('pos')))

    def get(self, pos):
        if 'pos'== 'QB':
            return self.qb
        elif 'pos' == 'RB':
            return self.rb
        elif 'pos' == 'WR':
            return self.wr
        elif 'pos' == 'TE':
            return self.te
        elif 'pos' == 'FLEX':
            return self.flex
        elif 'pos' == 'DST':
            return self.dst
        else:
            raise ValueError('player does not exist: {}'
                              .format(pos))

    def remove(self, player):
        if player.get('pos') == 'QB':
            if self.qb == player:
                self.qb = None
        elif player.get('pos') == 'WR':
            if player in self.wr:
                self.wr.remove(player)
            elif self.flex == player:
                self.flex = None 
        elif player.get('pos') == 'RB':
            if player in self.rb:
                self.rb.remove(player)
            elif self.flex == player:
                self.flex = None 
        elif player.get('pos') == 'TE':
            if self.te == player:
                self.te = None
        elif player.get('pos') == 'DST':
            if self.dst == player:
                self.dst = None
        elif player.get('pos') == 'FLEX':
            if self.flex == player:
                self.flex = None           
        else:
            raise ValueError('player does not exist: {}'
                              .format(player))

class PreseasonDfs(object):

    def __init__(self, players):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.flex = ('WR', 'TE', 'RB')
        self.lineups = []
        self.players = players       
        d = OrderedDict()
        d['QB'] = 1
        d['RB'] = 2
        d['WR'] = 3
        d['TE'] = 1
        d['FLEX'] = 1
        d['DST'] = 1
        self.positions = d

    @property
    def dsts(self):
        return [p for p in self.players if p['pos'] == 'DST']

    @property
    def flexs(self):
        return [p for p in self.players if p['pos'] in self.flex]

    @property
    def qbs(self):
        return [p for p in self.players if p['pos'] == 'QB']

    @property
    def rbs(self):
        return [p for p in self.players if p['pos'] == 'RB']

    @property
    def tes(self):
        return [p for p in self.players if p['pos'] == 'TE']

    @property
    def wrs(self):
        return [p for p in self.players if p['pos'] == 'WR']
  
    def random_stack(self):
        lu = Lineup()
        for pos, posnum in self.positions.items():
            while len(lu.get(pos)) < posnum:
                if pos in self.flex:
                    eligible = [p for p in self.flexs if p.get('team') == lu.qb['team']]
                    if eligible:
                        lu.add(random.choice(eligible))
                    else:
                        lu.add(self.player(pos, lu))
                else:
                    lu.add(self.player(pos, lu))
                i += 1
        return lu

    def player(self, pos, lineup=None):
        '''
        Returns random unused player from pool
        '''
        if not lineup:
            lineup = Lineup()

        currpos = lineup.get(pos)
        if currpos:
            if pos in self.flex:
                return random.choice([p for p in self.pool(pos)
                        if p not in currpos])
            else:
                 = p['name']
                return random.choice([p for p in self.pool(pos)
                                      if p['name'] != currpos])
        else:
            return random.choice([p for p in self.pool(pos)]) 

    def pool(self, pos):
        if pos == 'FLEX':
            return [p for p in self.players if p['pos'] in self.flex] 
        else:
            return [p for p in self.players if p['pos'] == pos]


if __name__ == '__main__':
    pass
