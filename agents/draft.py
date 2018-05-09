import logging

from nfl.parsers.draft import DraftNFLParser
from nfl.scrapers.draft import DraftNFLScraper
from nfl.seasons import get_season
from nfl.utility import pair_list


class DraftNFLAgent(object):
    '''
    '''

    def __init__(self, cc_headers, draft_headers, cache_name='draft-nfl-agent'):
        self._s = DraftNFLScraper(cache_name=cache_name)
        self._p = DraftNFLParser()
        self.cc_headers = cc_headers
        self.draft_headers = draft_headers

    def complete_contests(self, cc_headers):
        '''
        Gets complete_contests resource, saves to db

        Args:
            cc_headers (dict): 

        Returns:
            list: of dict
            
        '''
        pass

    def draft(self, headers):
        '''
        Gets complete_contests resource, saves to db
    
        Args:
            headers (dict): 
    
        Returns:
            list: of dict
    
        '''
        pass


if __name__ == '__main__':
    pass