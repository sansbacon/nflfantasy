import json
import logging


class FantasyLabsNFLParser():
    '''
    FantasyLabsNFLParser

    Usage:

        from FantasyLabsNFLScraper import FantasyLabsNFLScraper
        from FantasyLabsNFLParser import FantasyLabsNFLParser
        s = FantasyLabsNFLScraper()
        p = FantasyLabsNFLParser()

        # games
    '''

    def __init__(self):
        '''

        '''
        logging.getLogger(__name__).addHandler(logging.NullHandler())
                        

    def games(self, content, **kwargs):
        '''
        Parses json that is list of games

        Usage:
            games = p.games(games_json)
            games = p.games(games_json, omit=[])

        '''

        if 'omit' in kwargs:
            omit = kwargs['omit']

        else:
            omit = ['ErrorList', 'ReferenceKey', 'HomePrimaryPlayer', 'VisitorPrimaryPlayer', 'HomePitcherThrows', 'VisitorPitcherThrows','LoadWeather', 'PeriodDescription', 'IsExcluded' 'AdjWindBearing', 'AdjWindBearingDisplay', 'SelectedTeam', 'IsWeatherLevel1', 'IsWeatherLevel2', 'IsWeatherLevel3', 'WeatherIcon', 'WeatherSummary', 'EventWeather', 'EventWeatherItems', 'UseWeather']

        games = []

        try:
            parsed = json.loads(content)

        except:
            logging.error('parser.today(): could not parse json')
            return None

        if parsed:
            for item in parsed:
                game = {k:v for k,v in item.items() if not k in omit}
                games.append(game)
            
        return games

    def model(self, content, site='dk', season_year=None, week=None):
        '''
        Parses json associated with model (player stats / projections)

        Args:
            content (dict): parsed JSON
            season_year (int): 2018, etc.
            week (int): 1, etc.

        '''
        players = {}
        omit_properties = ['IsLocked']
        omit_other = ['ErrorList', 'LineupCount', 'CurrentExposure', 'ExposureProbability',
                      'IsExposureLocked', 'Positions', 'PositionCount', 'Exposure', 'IsLiked', 'IsExcluded']

        # models have nested dict in 'Properties'
        for playerdict in content.get('PlayerModels', []):
            player = {}
            if season_year:
                player['season_year'] = season_year
            if week:
                player['week'] = week

            for k,v in playerdict.items():
                if k == 'Properties':
                    for k2,v2 in v.items():
                        # trying to get integers for ownership %
                        if k2 == 'p_own':
                            try:
                                minown, maxown = v2.split('-')
                                player['p_own_min'] = minown
                                player['p_own_max'] = maxown
                            except:
                                try:
                                    minown = float(v2)
                                    maxown = float(v2)
                                    player['p_own_min'] = minown
                                    player['p_own_max'] = maxown
                                except:
                                    pass
                            player['p_own'] = v2
                        elif not k2 in omit_properties:
                            player[k2] = v2
                elif not k in omit_other:
                    player[k] = v
            # test if already have this player
            # use list where 0 index is DK, 1 FD, 2 Yahoo
            pid = player.get('PlayerId', None)
            pid_players = players.get(pid, [])
            pid_players.append(player)
            players[pid] = pid_players

        # The model has 3 dicts for each player: DraftKings, FanDuel, Yahoo
        # SourceIds: 4 is DK, 11 is Yahoo, 3 is FD
        if site:
            site_players = []
            site_ids = {'dk': 4, 'fd': 3, 'yahoo': 11}               
            for pid, player in players.items():
                for p in player:
                    if p.get('SourceId', 1) == site_ids.get(site, 2):
                        site_players.append(p)
            players = {p['Player_Name']:p for p in site_players if p.get('Player_Name')}
        return list(players.values())

    def dk_salaries(self, content, season, week, db=True):
        '''
        Gets list of salaries for insertion into database
        Args:
            content (str):
            season (int):
            week (int):
            db (bool):

        Returns:
            players (list): of player dict
        '''

        site = 'dk'
        wanted = ['Score', 'Player_Name', 'Position', 'Team', 'Ceiling', 'Floor', 'Salary', 'AvgPts', 'p_own', 'PlayerId']
        salaries = [{k:v for k,v in p.items() if k in wanted} for p in self.model(content, site=site)]

        # add columns to ease insertion into salaries table
        if db:
            fixed = []
            for salary in salaries:
                fx = {'source': 'fantasylabs', 'dfs_site': site, 'season_year': season, 'week': week}
                fx['source_player_id'] = salary.get('PlayerId')
                fx['source_player_name'] = salary.get('Player_Name')
                fx['salary'] = salary.get('Salary')
                fx['team'] = salary.get('Team')
                fx['dfs_position'] = salary.get('Position')
                fixed.append(fx)
            salaries = fixed

        return salaries

if __name__ == "__main__":
    pass
