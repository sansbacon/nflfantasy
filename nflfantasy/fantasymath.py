'''

# nflfantasy/fantasymath.py
# scraper/parser for fantasymath.com fantasy resources

'''

import logging
import time

from sportscraper.scraper import RequestScraper


class Scraper(RequestScraper):
    '''

    '''

    def __init__(self, **kwargs):
        '''
        Scrape fantasymath API

        Args:

        '''
        RequestScraper.__init__(self, **kwargs)
        self.headers.update({'origin': 'https://fantasymath.com',
                             'authority': 'api.fantasymath.com',
                             'referer': 'https://fantasymath.com/'})

    def distribution(self, player_codes):
        '''
        Gets projection distribution for specified players

        Args:
            player_codes(list): of str

        Returns:
            dict

        '''
        # api uses multiple parameters with same key (wdis)
        # get_json method sorts params for caching consistency
        # need to use tuple of lists so not overwrite wdis param
        player_codes = list(player_codes)
        url = 'https://api.fantasymath.com/v2/players-wdis/'
        wdis = tuple(['wdis', player_code] for player_code in player_codes)
        params = (['dst', 'mfl'], ['qb', 'pass4'], ['scoring', 'ppr'])
        resp = self.session.get(url, params=wdis + params)
        self.urls.append(resp.url)
        resp.raise_for_status()
        if self.delay:
            time.sleep(self.delay)
        return resp.json()

    def players(self):
        '''
        Gets projection distribution for specified players

        Args:
            player_codes(list): of str

        Returns:
            dict

        '''
        url = 'https://api.fantasymath.com/players'
        return self.get_json(url)


class Parser():
    '''
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _fix_val(self, v):
        '''
        Fixes various values

        Args:
            v:

        Returns:

        '''
        try:
            return round(v, 3)
        except:
            return v

    def distribution(self, content):
        '''
        Parses player distribution JSON

        Args:
            content (dict): parsed JSON

        Returns:
            list: of player dict

        '''
        wanted = ['fp_id', 'name', 'p25', 'p5', 'p50', 'p75', 'p95', 'pos', 'prob',
                  'proj', 'scoring', 'std']
        return [{k: self._fix_val(v) for k,v in p.items() if k in wanted} for
                p in content['players']]


    def players(self, content):
        '''
        Parses players JSON

        Args:
            content (dict): parsed JSON

        Returns:
            dict

        '''
        fm_players = {}
        for p in content:
            vals = p['label'].split()
            d = {'id': p['value'], 'pos': vals[0], 'name': ' '.join(vals[1:])}
            fm_players[d['id']] = d
        return fm_players


class Agent():
    '''
    '''

    def __init__(self, cache_name='fantasymath-agent'):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._s = Scraper(cache_name=cache_name, delay=1.5)
        self._p = Parser()

    def weekly_projections(self):
        '''
        Gets weekly projections

        Args:
            None

        Returns:
            dict

        '''
        dists = {}
        content = self._s.players()
        players = self._p.players(content)

        for i in range(0, len(players), 3):
            try:
                ids = [players[i]['id'], players[i+1]['id'], players[i+2]['id']]
            except IndexError:
                try:
                    ids = [players[i]['id'], players[i+1]['id']]
                except:
                    ids = [players[i]['id']]
            idstr = ', '.join(ids)
            logging.info('getting %s', idstr)
            if idstr in dists:
                logging.info('skipping %s', idstr)
                continue
            try:
                content = self._s.distribution(ids)
                dists[idstr] = self._p.distributions(content)
            except:
                logging.exception('could not get %s', idstr)
        return dists


if __name__ == '__main__':
    pass
