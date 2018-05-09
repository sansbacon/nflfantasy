# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import logging
import math
import re
import xml.etree.ElementTree as ET


class FantasyFootballCalculatorParser():
    '''
    Parses html of NFL fantasy projections page of fantasycalculator.com into player dictionaries

    Example:
        p = FantasyFootballCalculatorParser()
        players = p.projections(content)
    '''

    def __init__(self):
        '''
        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self.positions = ['QB', 'RB', 'WR', 'TE']

    def _fix_header(self, header):
        '''
        Looks at global list of headers, can provide extras locally
        :param headers:
        :return:
        '''

        fixed = {
            'id': 'ffcalculator_id',
            'rk': 'overall_rank',
            'avg': 'fantasy_points_per_game',
        }

        #return fixed.get(header, header)
        fixed_header = self._fix_header(header)

        # fixed_header none if not found, so use local list
        if not fixed_header:
            return fixed.get(header, header)

        else:
            return fixed_header

    def _fix_headers(self, headers):
        '''

        :param headers:
        :return:
        '''
        return [self.fix_header(header) for header in headers]

    def _to_overall_pick(self, adp, adp_league_size, my_league_size):
        '''
        Data is in 2.01 format, so you have to translate those numbers to an overall pick
        
        :param adp(str): is in round.pick format
        :param adp_league_size(int): number of teams in types of draft (8, 10, 12, 14)
        :return: Dictionary: is overall, round, pick based on your league size
        '''
        round, pick = adp.split('.')
        overall_pick = ((int(round) - 1) * adp_league_size) + int(pick)
        adjusted_round = math.ceil(overall_pick/float(my_league_size))
        if adjusted_round == 1:
            adjusted_pick = overall_pick
        else:
            adjusted_pick = overall_pick - ((adjusted_round - 1) * my_league_size)
        return {'overall_pick': overall_pick, 'round': adjusted_round, 'pick': adjusted_pick}

    def adp_old(self, content):
        '''
        Gets ADP from past seasons

        Args:
            content: 

        Returns:
            list of dict
        '''
        results = []
        soup = BeautifulSoup(content, 'lxml')
        t = soup.find('table', class_=['table', 'adp'])
        headers = ['rank', 'pick', 'source_player_name', 'pos', 'team_code', 'overall', 'stdev', 'high', 'low', 'n']
        for tr in t.find_all('tr'):
            if tr.has_attr('class'):
                vals = [td.text for td in tr.find_all('td')[:-1]]
                results.append(dict(zip(headers, vals)))
            else:
                pass

        return results

    def adp (self, xml, size=12):
        '''
        Parses xml and returns list of player dictionaries
        Args:
            content (str): xml typically fetched by FantasyCalculatorNFLScraper class
        Returns:
            List of dictionaries if successful, empty list otherwise.
        '''
        players = []
        root = ET.fromstring(xml)
        adp_league_size = int(root.find('.//teams').text)
        for item in root.findall('.//player'):
            if item.find('./pos').text.lower() == 'pk':
                pass
            else:
                player = {'source': 'ffcalc'}
                for child in item.findall('*'):
                    if child.tag.lower() == 'adp':
                        fixed = self._to_overall_pick(child.text, adp_league_size, size)
                        player['overall_pick'] = fixed['overall_pick']
                        player['round'] = int(fixed['round'])
                        player['pick'] = int(fixed['pick'])
                    else:
                        player[child.tag.lower()] = child.text
                players.append(player)
        return players

    def projections (self,content):
        '''
        Parses all rows of html table using BeautifulSoup and returns list of player dictionaries
        Args:
            content (str): html table typically fetched by FantasyCalculatorNFLScraper class
        Returns:
            List of dictionaries if successful, empty list otherwise.
        '''

        players = []
        headers = []

        soup = BeautifulSoup(content)
        table = soup.find('table', {'id': 'rankings-table'})

        for th in table.findAll('th'):
            value = th.string.lower()

            if re.match(r'\d+', value):
                headers.append('week%s_projection' % value)
            else:
                headers.append(value)

        headers = self.fix_headers(headers)

        # players - use regular expression to include header row (which has no class)
        for row in table.findAll('tr', {'class': re.compile(r'\w+')}):
            self.logger.debug(row)
            tds = [td.string for td in row.findAll("td")]
            player = dict(zip(headers, tds))

            # exclude unwanted positions from results
            if player.get('position') in self.positions:
                players.append(player)
            else:
                self.logger.info('excluded %s because %s' % (player.get('full_name'), player.get('position')))

        return players

if __name__ == '__main__':
    pass

