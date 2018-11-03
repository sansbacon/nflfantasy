import json
import logging


class FantasyMathParser(object):
    '''
    FantasyMathParser

    Usage:


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
        if isinstance(v, float):
            return round(v, 2)
        else:
            return v


    def distributions(self, content):
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


if __name__ == "__main__":
    pass
