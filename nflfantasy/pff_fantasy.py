'''

# nflfantasy/pff_fantasy.py
# scraper/parser for profootballfocus.com fantasy resources

'''

import logging

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):
    '''
    Scraper for profootballfocus.com fantasy resources

    '''
    def bestball(self):
        '''
        Gets profootballfocus teams

        Returns:
            dict

        '''
        return self.get_json('https://www.profootballfocus.com/api/prankster/rankings/nfl-best-ball')

    def weekly_projections(self, week):
        '''
        Gets profootballfocus weekly projections

        Args:
            week(int): NFL week, 1-17

        Returns:
            dict

        '''
        url = 'https://www.profootballfocus.com/api/prankster/projections?'
        params = {'scoring': 54574, 'weeks': week}
        return self.get_json(url, payload=params)


class Parser():
    '''
    Parser for profootballfocus.com fantasy resources


    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    @staticmethod
    def _name(player):
        try:
            return f"{player['first_name']} {player['last_name']}"
        except:
            return None

    @staticmethod
    def _overall_rankings(rankings, playerposd):
        '''
        Gets overall rankings

        Args:
            rankings(dict):
            playerposd(dict):

        Returns:
            list: of dict

        '''
        vals = []
        position_rankings = rankings.get('position_rankings')
        overall_rankings = [r for r in position_rankings if
                            r['position'] == 'overall'][0]['player_rankings']
        pff_ranks = {r['player_id']: [rk['rank'] for rk in r['ranks']]
                     for r in overall_rankings}
        for key, value in pff_ranks.items():
            playerd = playerposd.get(key)
            if playerd:
                playerd['player_id'] = key
                playerd['ranks'] = sorted(value)
                if len(value) == 4:
                    playerd['avg'] = round(sum(value[1:3]) / 2.0, 2)
                else:
                    playerd['avg'] = round(sum(value) / float(len(value)), 2)
            vals.append(playerd)
        return vals

    @staticmethod
    def _player_names(rankings):
        '''
        Dictionary of player_id and name

        Args:
            rankings(dict):

        Returns:
            dict

        '''
        players = rankings['players']
        playerd = {}
        for p in players:
            playerd[p['player_id']] = Parser._name(p)
        return playerd

    @staticmethod
    def _player_positions(rankings):
        '''
        Dictionary of player_id and position

        Args:
            position_rankings(dict):

        Returns:
            dict

        '''
        player_position_d = {}
        position_rankings = rankings.get('position_rankings')
        for posrk in position_rankings:
            pos = posrk.get('position')
            if pos in ['overall', 'dst', 'k']:
                continue
            for rk in posrk.get('player_rankings'):
                player_position_d[rk.get('player_id')] = pos
        return player_position_d

    @staticmethod
    def _player_position_dict(playerd, posd):
        '''
        Merges player and position dicts

        '''
        playerposd = {}
        for k, v in playerd.items():
            pos = posd.get(k, '').upper()
            playerposd[k] = {'plyr': v, 'pos': pos}
        return playerposd

    def bestball_rankings(self, content):
        '''
        Parses pff bestball json document

        Args:
            content(dict): parsed json

        Returns:
            list: of dict

        '''
        playerd = Parser._player_names(content)
        posd = Parser._player_positions(content)
        playerposd = Parser._player_position_dict(playerd, posd)
        return Parser._overall_rankings(content, playerposd)

        """
        results = []

        # teams
        teams = content['teams']
        teams_d = {t['franchise_id']: t for t in teams}

        # ranking_type
        positions = content['ranking_type']['allowed_positions']
        ranking_type = content['ranking_type']['path']
        season = content['ranking_type']['season']

        # rankers
        rankers = content['rankers']
        rankers_d = {r['id']: r for r in rankers}

        # players
        players = content['players']
        players_d = {p['player_id']: p for p in players}

        # position_rankings
        for posrank in content['position_rankings']:
            pos = posrank['position']
            for prkg in posrank['player_rankings']:
                pid = prkg['player_id']
                for rnk in prkg['ranks']:
                    results.append({'source_player_id': pid,
                                    'source_player_name': self._name(players_d.get(pid)),
                                    'source_player_rank': rnk['rank'],
                                    'source_ranker_id': rnk['ranker_id'],
                                    'source_ranker_name': rankers_d[rnk['ranker_id']]['name'],
                                    'source_player_position': pos,
                                    'season_year': season, 'source_ranking_type': ranking_type})

        return results
        """

    def weekly_projections(self, content):
        '''
        Parses profootballfocus weekly projections

        Args:
            content(dict): parsed JSON

        Returns:
            list

        '''
        return content['player_projections']


class Agent():
    '''
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name)
        self._p = Parser()

    def weekly_projections(self, week):
        '''
        Gets PFF weekly projections

        Args:
            week(int):

        Returns:
            list: of dict

        '''
        content = self._s.weekly_projections(week)
        return self._p.weekly_projections(content)


if __name__ == '__main__':
    pass
