import logging
import re
import xml.etree.ElementTree as ET

from nba.utility import merge_many


class YahooNBAParser(object):

    def __init__(self):
        logging.getLogger(__name__).addHandler(logging.NullHandler())

    def _game_stat_categories(self, content):
        '''
        Parses stat_categories from game resource
        
        Args:
            content (str): 

        Returns:
            list: of dict
        '''

    def game(self, content, subresource='metadata'):
        '''
        Parses game resource
        
        Args:
            content (str): 

        Returns:
            dict

        '''
        # strip namespaces - not needed
        # then parse content2
        content2 = re.sub(r'\sxmlns="[^"]+"', '', str(content), count=1)
        root = ET.fromstring(content2)
        return [{child.tag: child.text for child in game} for game in root.iter('game')]

    def leagues(self, content):
        '''
        Parses leagues collection
        
        Args:
            content (str): XML 

        Returns:
            dict
            
        '''
        # strip namespaces - not needed
        # then parse content2
        content2 = re.sub(r'\sxmlns="[^"]+"', '', str(content), count=1)
        root = ET.fromstring(content2)
        return [{child.tag: child.text for child in league} for league in root.iter('league')]

    def salaries(self, content):
        '''
        Parses salaries JSON from yahoo DFS

        Args:
            content(dict): parsed JSON

        Returns:
            list: of dict

        '''
        players = content['players']['result']
        wanted = ['code', 'firstName', 'lastName', 'salary',
                  'primaryPosition', 'playerSalaryId']
        return [{k: v for k, v in p.items() if k in wanted} for p in players]

    def teams_json(self, content):
        '''
        Parses teams API call
        
        Args:
            content (dict): parsed JSON
        
        Returns:
            list: of dict
            
        '''
        results = []
        for k,v in content['fantasy_content']['league'][1]['teams'].items():
            t = []
            if k == 'count':
                continue
            else:
                for item in v['team'][0]:
                    if item:
                        t.append(item)
            results.append(merge_many({}, t))
        return results


if __name__ == '__main__':
    pass
