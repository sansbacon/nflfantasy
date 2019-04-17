'''
xref.py
provides classes for matching players across sites

'''
import abc
import logging
from collections import defaultdict

from playermatcher.match import player_match
from playermatcher.name import first_last


class Site(metaclass=abc.ABCMeta):
    '''
    Site subclasses should implement these methods
    https://stackoverflow.com/questions/372042/
    '''

    @abc.abstractmethod
    def get_mfld(self, first):
        '''
        Interface

        Returns:

        '''
        raise NotImplementedError('users must define get_mfld to use this base class')

    @abc.abstractmethod
    def get_players(self):
        '''
        Interface

        Returns:

        '''
        raise NotImplementedError('users must define get_players to use this base class')

    @abc.abstractmethod
    def get_playersd(self, key):
        '''
        Interface

        Returns:

        '''
        raise NotImplementedError('users must define get_playersd to use this base class')

    @abc.abstractmethod
    def match_mfl(self, mfl_players, id_key, name_key,
                  pos_key, interactive):
        '''
        Interface

        Returns:

        '''
        raise NotImplementedError('users must define match_mfl to use this base class')


class Fanball(Site):
    '''
    Used to cross-reference fanball players

    '''

    def __init__(self, db):
        '''

        Args:
            db(NFLPostgres): instance

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.db = db

    def add_xref(self, *players):
        '''
        Adds players to xref table

        Args:
            players: list of dict

        Returns:
            None

        '''
        # TODO: implement this
        pass

    def get_mfld(self, first='mfl'):
        '''
        Query database for dict to cross-reference fanball with mfl or vice versa

        Args:
            first(str): which site is first, default 'mfl'

        Returns:
            dict - mfl_player_id: fanball_id or vice versa

        '''
        q = """SELECT mfl_player_id as m, fb_player_id as f FROM dfs.fb_mfl_xref"""
        players = self.db.select_dict(q)
        if first == 'mfl':
            return {p['m']: p['f'] for p in players}
        return {p['m']: p['f'] for p in players}

    def get_players(self):
        '''
        Gets MFL players from salary table

        Returns:
            list

        '''
        q = """SELECT * FROM dfs.vw_fb_players"""
        return self.db.select_dict(q)

    def get_playersd(self, key='name'):
        '''
        Gets MFL players from salary table

        Args:
            key(str):

        Returns:
            dict

        '''
        d = defaultdict(list)
        q = """SELECT * FROM dfs.vw_fb_players"""
        if key == 'name':
            for p in self.db.select_dict(q):
                d[p['source_player_name']].append(p)
        elif key == 'namepos':
            for p in self.db.select_dict(q):
                k = '{}_{}'.format(p['source_player_name'], p['dfs_position'])
                d[k].append(p)
        else:
            raise ValueError('invalid key name: {}'.format(key))
        return d

    def match_mfl(self, mfl_players, id_key, name_key,
                  pos_key=None, interactive=False):
        '''
        Matches mfl players to fanball players

        Args:
            mfl_players(list):
            id_key(str):
            name_key(str):
            pos_key(str):
            interactive(bool):

        Returns:
            list: of player

        '''
        d = self.get_mfld(first='mfl')
        fbd = self.get_playersd('name')
        fb_playernames = list(fbd.keys())

        for idx, p in enumerate(mfl_players):
            # first option is to see if already in database
            if d.get(p[id_key]):
                mfl_players[idx]['fb_player_id'] = d[p[id_key]]
                continue

            # if not in database, use matcher
            # player
            match_name = player_match(first_last(p[name_key]), fb_playernames, thresh=90,
                                      interactive=interactive)
            match = fbd.get(match_name)
            if match and len(match) == 1:
                mfl_players[idx]['fb_player_id'] = match[0]['fb_player_id']
        return mfl_players


class F4f(Site):
    '''
    Used to cross-reference 4-for-4 players

    '''

    def __init__(self, db):
        '''

        Args:
            db(NFLPostgres): instance

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.db = db

    def add_xref(self, *players):
        '''
        Adds players to xref table

        Args:
            players: list of dict

        Returns:
            None

        '''
        # TODO: implement this
        pass

    def get_mfld(self, first='mfl'):
        '''
        Query database for dict to cross-reference fanball with mfl or vice versa

        Args:
            first(str): which site is first, default 'mfl'

        Returns:
            dict - mfl_player_id: fanball_id or vice versa

        '''
        q = """SELECT mfl_player_id as m, f4f_player_id as f FROM dfs.f4f_mfl_xref"""
        players = self.db.select_dict(q)
        if first == 'mfl':
            return {p['m']: p['f'] for p in players}
        return {p['m']: p['f'] for p in players}

    def get_players(self):
        '''
        Gets MFL players from salary table

        Returns:
            list

        '''
        q = """SELECT * FROM dfs.vw_f4f_players"""
        return self.db.select_dict(q)

    def get_playersd(self, key='name'):
        '''
        Gets MFL players from salary table

        Args:
            key(str):

        Returns:
            dict

        '''
        d = defaultdict(list)
        q = """SELECT * FROM dfs.vw_f4f_players"""
        if key == 'name':
            for p in self.db.select_dict(q):
                d[p['source_player_name']].append(p)
        elif key == 'namepos':
            for p in self.db.select_dict(q):
                k = '{}_{}'.format(p['source_player_name'], p['dfs_position'])
                d[k].append(p)
        else:
            raise ValueError('invalid key name: {}'.format(key))
        return d

    def match_mfl(self, mfl_players, id_key, name_key,
                  pos_key=None, interactive=False):
        '''
        Matches mfl players to fanball players

        Args:
            mfl_players(list):
            id_key(str):
            name_key(str):
            pos_key(str):
            interactive(bool):

        Returns:
            list: of player

        '''
        d = self.get_mfld(first='mfl')
        f4fd = self.get_playersd('name')
        f4f_playernames = list(f4fd.keys())

        for idx, p in enumerate(mfl_players):
            # first option is to see if already in database
            if d.get(p[id_key]):
                mfl_players[idx]['f4f_player_id'] = d[p[id_key]]
                continue

            # if not in database, use matcher
            # player
            match_name = player_match(first_last(p[name_key]), f4f_playernames, thresh=90,
                                      interactive=interactive)
            match = f4fd.get(match_name)
            if match and len(match) == 1:
                mfl_players[idx]['f4f_player_id'] = match[0]['f4f_player_id']

        return mfl_players


if __name__ == '__main__':
    pass
