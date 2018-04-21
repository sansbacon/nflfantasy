import datetime
import itertools
import logging
import time

import pandas as pd


from nfl.parsers.fantasypros import FantasyProsNFLParser
from nfl.scrapers.fantasypros import FantasyProsNFLScraper
from nfl.seasons import get_season
from nfl.utility import pair_list


class FantasyProsNFLAgent(object):
    '''
    Usage:
        import pickle
        logging.basicConfig(level=logging.INFO)
        a = FantasyProsNFLAgent()
        players = a.weekly_rankings_archived()
        with open('fpros-archive.pkl', 'wb') as outfile:
        pickle.dump(players, outfile)
    '''

    def __init__(self, cache_name='fpros-nfl-agent'):
        self._s = FantasyProsNFLScraper(cache_name=cache_name)
        self._p = FantasyProsNFLParser()


    def weekly_rankings_archived(self):
        '''
        Gets old fantasypros rankings from the wayback machine
        Uses wayback API to figure out if week rankings exist, then fetch+parse result

        Returns:
            players(list): of player rankings dict
        '''
        players = []
        base_fpros = 'https://www.fantasypros.com/nfl/rankings/{}.php'
        positions = ['QB', 'RB', 'WR', 'TE']

        # loop through seasons
        for season in [2014, 2015]:

            # s is dict with keys = week, dict with keys start, end as value
            s = get_season(season)

            # loop through weeks
            for week, v in s.items():
                if s.get(week, None):
                    weekdate = s.get(week)
                    if weekdate:
                        d = weekdate.get('start')
                        logging.debug('d is a {}'.format(type(d)))
                    else:
                        raise Exception ('could not find start of {} week {}'.format(season, week))

                # loop through positions
                for pos in positions:

                    # generate url for wayback machine
                    fpros_url = base_fpros.format(pos)
                    content, cached = self._wb(fpros_url, d)

                    if content:
                        pw = self._p.weekly_rankings(content, season, week, pos)
                        logging.info(pw)
                        players.append(pw)
                    else:
                        logging.error('could not get {}|{}|{}'.format(season, week, pos))

                    if not cached:
                        time.sleep(2)

        # players is list of list, flatten at the end
        return list(itertools.chain.from_iterable(players))

    def weekly_rankings(self, season, week, flex=False):
        '''
        Gets current fantasypros rankings

        Returns:
            players(list): of player rankings dict
        '''
        # this doesn't work

        '''
        players = []
        base_fpros = 'https://www.fantasypros.com/nfl/rankings/{}.php'
        positions = ['qb', 'rb', 'wr', 'te', 'flex']

        # loop through seasons
        # loop through positions
        for pos in positions:
            if not flex and pos == 'flex':
                continue

            content = self._s.get(base_fpros.format(pos))

            if content:
                pw = self._p.weekly_rankings(content, season, week, pos)
                logging.info(pw)
                players.append(pw)
            else:
                logging.error('could not get {}|{}|{}'.format(season, week, pos))

        # players is list of list, flatten at the end
        if not flex:
            return list(itertools.chain.from_iterable(players))
        else:
            return list(itertools.chain.from_iterable(players)), flex_players
        '''


    def expert_weekly_rankings(self, season, week, pos, expert):
        '''
        Gets weekly rankings from expert
                
        Args:
            season: 
            week: 
            pos: 
            expert:

        Returns:
            list: of dict

        '''
        # NOTE: should move this to a function
        # also need to figure out if can obtain old ones by week
        # step one: get the fantasypros list of players
        # then filter out lower-ranked players with ECR threshold
        posthresh = {'QB': 20, 'RB': 50, 'WR': 70, 'TE': 14, 'DST': 20, 'K': 14}
        pcontent = self._s.get_json(url='https://www.fantasypros.com/ajax/player-search.php',
                                    payload={'sport': 'NFL', 'position_id': 'OP'})

        # add positional ranks and then filter by positional threshold
        playerdf = pd.DataFrame(pcontent)
        playerdf.drop(['filename', 'value'], axis=1, inplace=True)
        poscrit = playerdf['position'].isin(posthresh.keys())
        playerdf = playerdf[poscrit]
        playerdf.dropna(subset=['ecr'], inplace=True)
        playerdf['posrk'] = playerdf.groupby("position")["ecr"].rank()
        playerdf['thresh'] = playerdf['position'].apply(
            lambda x: posthresh.get(x, None))
        threshcrit = playerdf['posrk'] <= playerdf['thresh']
        playerdf = playerdf[threshcrit]
        playerdf.sort_values(by=['position', 'posrk'], inplace=True)

        # now do pairs of players
        compare_url = 'https://partners.fantasypros.com/api/v1/compare-players.php?'
        expert_ranks = []

        for pair in pair_list(playerdf.itertuples()):
            if (pair[0][4] != pair[1][4]):
                raise ValueError('pairs have different positions: {}'.format(pair))
            player_pair = '{}:{}'.format(pair[0][2], pair[1][2])
            pos = pair[0][4]

            # players are colon-separated ids (13926:16421)
            # expert 120 is Sean Koerner
            params = {
                'players': player_pair,
                'experts': expert,
                'position': pos,
                'ranking_type': '1',
                'details': 'all',
                'sport': 'NFL',
                'callback': 'FPWSIS.compareCallback'
            }

            content = self._s.get(url=compare_url, payload=params)
            pair_rank = self._p.expert_rankings(content)
            expert_ranks.append(pair_rank)

        return expert_ranks


if __name__ == '__main__':
    pass
