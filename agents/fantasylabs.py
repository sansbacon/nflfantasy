from __future__ import print_function

import csv
import logging
from random import choice, uniform
import time

from nfl.scrapers.fantasylabs import FantasyLabsNFLScraper
from nfl.parsers.fantasylabs import FantasyLabsNFLParser
from nfl.optimizers.optimize import run_solver
from nfl.optimizers.orm import ORToolsPlayer
from nfl.projections import alter_projection


class FantasyLabsNFLAgent(object):
    '''

    Usage:
        # to access paid stats, you will need a cookie library
        import browsercookie

        # uses cache to reduce API calls
        a = FantasyLabsNFLAgent(cache_name='/home/sansbacon/.rcache/fantasylabs-nfl2', cj=browsercookie.firefox())

        # get list of players with projections
        players = a.model('1_4_2017', 'levitan', 'dk')

        # optimize
        for l in a.optimize(players=players, projection_formula='cash'):
            print ('Iteration {}-{}'.format(l['iteration_id'], l['team_id']))
            print(l['players'])
    '''


    def __init__(self, cache_name=None, cj=None):
        logging.getLogger(__name__).addHandler(logging.NullHandler())
        self._p = FantasyLabsNFLParser()
        self._s = FantasyLabsNFLScraper(cookies=cj, cache_name=cache_name)

    def _genalg_players(self, players, projection_formula, team_exclude=[], player_exclude=[],
                           randomize_projections=True, ownership_penalty=False):
        '''
        TODO: not implemented
        Takes list of player dicts, returns list of Player objects for use in optimizer

        Args:
            players:
            projection_formula:
            team_exclude:
            player_exclude:
            randomize_projections:
            ownership_penalty:

        Returns:

        '''

        all_players = []
        return all_players

    def _optimizer_players(self, players, projection_formula, team_exclude=[], player_exclude=[],
                           randomize_projections=True, ownership_penalty=False):
        '''
        Takes list of player dicts, returns list of Player objects for use in optimizer

        Args:
            players:
            projection_formula:
            team_exclude:
            player_exclude:
            randomize_projections:
            ownership_penalty:

        Returns:
            all_players(list): of Player objects
        '''

        all_players = []

        for p in players:
            oppos = str(p.get('Opposing_TeamFB', '').replace('@', ''))
            pos = str(p.get('Position'))
            if pos == 'D': pos = str('DST')
            team = str(p.get('Team'))
            player_name = str(p.get('Player_Name'))
            code = str('{}_{}'.format(player_name, pos))

            mean_projection = p.get('AvgPts', 0)
            ceiling = p.get('Ceiling', 0)
            floor = p.get('Floor', 0)

            # can add random element to projections, helpful if generating a lot of lineups
            if randomize_projections:
                projections, ceilings, floors = self._randomize_projections(mean_projection, ceiling, floor)
            else:
                projections = [mean_projection]
                ceilings = [ceiling]
                floors = [floor]

            proj = self._projection_formula(projections, ceilings, floors, projection_formula)
            if ownership_penalty:
                proj = self._ownership_penalty(proj, p.get('p_own'))

            # uses team_exclude and player_exclude at the pool level rather than optimizer level
            # easier to control inputs and less optimizer code
            if team in team_exclude:
                continue
            elif player_name in player_exclude:
                continue
            else:
                p = ORToolsPlayer(proj=proj, matchup=p.get('Opposing_TeamFB'), opps_team=oppos, code=code, pos=pos,
                           name=player_name, cost=p.get('Salary'), team=team)
                all_players.append(p)

        return all_players

    def _ownership_penalty(self, proj, pown):
        '''
        TODO: this is not production-ready
        Args:
            proj:
            pown:

        Returns:

        '''
        if pown:
            if '-' in pown:
                min, max = pown.split('-')
                o = (float(min) + float(max)) / 2
                proj = (1 - o) ** 2 * proj / 10 + proj
            else:
                try:
                    o = float(pown)
                    proj = (1 - o) ** 2 * proj / 10 + proj
                except:
                    logging.debug('could not adjust for ownership')

        else:
            logging.debug('could not adjust for ownership')

        return proj

    def _projection_formula(self, projections, ceilings, floors, projection_formula):
        '''
        Alters projections based on projection formula

        Args:
            projections:
            ceilings:
            floors:
            projection_formula:

        Returns:
            proj(float): single projection for use in optimizer
        '''

        # specify weights for mean, ceiling, and floor
        # have 3 preset weights: cash, tournament, tourncash
        if projection_formula == 'cash':
            proj = (choice(projections) * .5) + (choice(ceilings) * .15) + (choice(floors) * .35)
        elif projection_formula == 'tournament':
            proj = (choice(projections) * .3) + (choice(ceilings) * .6) + (choice(floors) * .1)
        elif projection_formula == 'tourncash':
            proj = (choice(projections) * .4) + (choice(ceilings) * .3) + (choice(floors) * .3)
        elif ',' in projection_formula and len(projection_formula.split(',')) == 3:
            avg, ceiling, floor = [float(i) for i in projection_formula.split(',')]
            proj = (choice(projections) * avg) + (choice(ceilings) * ceiling) + (choice(floors) * floor)
        else:
            proj = choice(projections)

        return proj

    def _randomize_projections(self, mean_projection, ceiling, floor):
        '''
        Adds some random noise to projections
        Args:
            mean_projection:
            ceiling:
            floor:

        Returns:

        '''
        projections = [mean_projection + round(mean_projection * uniform(-.05, .05), 2) for i in range(0, 5)]
        ceilings = [ceiling + round(ceiling * uniform(-.05, .05), 3) for i in range(0, 5)]
        floors = [floor + round(floor * uniform(-.05, .05), 3) for i in range(0, 5)]
        return (projections, ceilings, floors)

    def genalg(self, players, n=5, projection_formula='cash', player_exclude=[], team_exclude=[], randomize_projections=True, ownership_penalty=False):
        '''
        TODO: not implemented
        Uses genetic algorithm, returns list of n lineups

        Args:
            players(list): list of player dict
            n(int): number of lineups
            projection_formula(str): can be specific name or comma-separated values of weights
            player_exclude: can be list or filename
            team_exclude: can be list or filename

        Returns:
            lineups
        '''

        if player_exclude:
            if isinstance(player_exclude, basestring):
                player_exclude = [l.strip() for l in open(player_exclude, 'r').readlines()]

        if team_exclude:
            if isinstance(team_exclude, basestring):
                team_exclude = [l.strip() for l in open(team_exclude, 'r').readlines()]

        return player_exclude, team_exclude

    def model(self, model_date, model_name, site):
        '''
        Takes date, name, and site for model, returns list of player dict
        Args:
            model_date:
            model_name:
            site:

        Returns:

        '''
        model = self._s.model(model_date, model_name)
        return self._p.model(model, site)

    def models(self):
        '''
        TODO: not implemented
        can get range of old models & salaries

        Returns:
            players(list): of player dict
        '''
        import datetime
        logging.basicConfig(level=logging.DEBUG)
        a = FantasyLabsNFLAgent()
        fmt = '%m_%d_%Y'

        seasons = {2016: {}, 2015: {}, 2014: {}}

        for season in [2016, 2015, 2014]:
            if season == 2016:
                start = datetime.datetime.strptime('09_07_2016', fmt)
                for week in range(1, 14):
                    d = datetime.datetime.strftime(start + datetime.timedelta(days=(week - 1) * 7), fmt)
                    seasons[season][week] = d
                    logging.debug(seasons[season], seasons[season][week])

            elif season == 2015:
                start = datetime.datetime.strptime('09_09_2015', fmt)
                for week in range(1, 18):
                    d = datetime.datetime.strftime(start + datetime.timedelta(days=(week - 1) * 7), fmt)
                    seasons[season][week] = d
                    logging.debug(seasons[season], seasons[season][week])

            elif season == 2014:
                start = datetime.datetime.strptime('09_03_2014', fmt)
                for week in range(1, 18):
                    d = datetime.datetime.strftime(start + datetime.timedelta(days=(week - 1) * 7), fmt)
                    seasons[season][week] = d
                    logging.debug(seasons[season], seasons[season][week])


    def optimize(self, players, projection_formula, i=2, n=5,
                 player_exclude=[], team_exclude=[],
                 randomize_projections=True, ownership_penalty=False):
        '''
        Returns list of n lineups per i iteration
        If you want 20 lineups, you could make i=20 and n=1 or i=4 and n=5
        All of the n in each i will use the same projections, the i groups use different ones

        Args:
            players(list): list of player dict
            n(int): number of lineups
            i(int): number of iterations
            projection_formula(str): can be specific name or comma-separated values of weights
            player_exclude: can be list or filename
            team_exclude: can be list or filename
            randomize_projections(bool): add some random noise
            ownership_penalty(bool): adjust projections based on ownership

        Returns:
            lineups
        '''
        results = {}

        # can use textfiles for excludes
        if player_exclude:
            if isinstance(player_exclude, basestring):
                player_exclude = [l.strip() for l in open(player_exclude, 'r').readlines()]

        if team_exclude:
            if isinstance(team_exclude, basestring):
                team_exclude = [l.strip() for l in open(team_exclude, 'r').readlines()]

        # loop through iteration groups
        for x in xrange(0, i):
            # put the players in the right format for optimizer
            p = self._optimizer_players(players, projection_formula=projection_formula,
                       player_exclude=player_exclude, team_exclude=team_exclude, randomize_projections=True)

            # n is number of teams per iteration (teams run with the same projections)
            for idx, roster in enumerate(run_solver(p, depth=n)):
                roster_id = '{}-{}'.format(x, idx)
                results[roster_id] = roster

        # iteration_id, team_id, players
        return results

    def pivots(self, players, sal_av=300, proj_av=.10, thresholds={'QB': 16, 'RB': 12, 'WR': 12, 'TE': 8, 'DST': 6}):
        '''
        TODO: not fully implemented
        Identifies potential pivot plays at similar salary with lower ownership

        Args:
            players:
            sal_av:
            proj_av:
            thresholds:

        Returns:
            pivots(dict): key is player_name, value is list of player dicts
        '''

        ps = {}

        for p in players:
            nm = p.get('Player_Name')
            pos = p.get('Position')
            sal = p.get('Salary')
            proj = p.get('AvgPts')

            if pos and sal and proj:
                if proj < thresholds.get(pos):
                    continue
                else:
                    ps[nm] = [mp for mp in players if mp.get('Position') == pos
                              and abs(mp.get('Salary') - sal) <= sal_av
                              and abs(mp.get('AvgPts') - proj <= proj * proj_av)
                              and mp.get('AvgPts') >= 8
                              and mp.get('Player_Name') != nm]

        return ps

    def r_pipeline(self, players=[], model_date=None, fn=None, model_name='levitan', site='dk', projection_formula=None, randomize=False):
        '''
        Takes fantasylabs projections, creates list / csv file for R analysis and optimizer
        Args:
            model_date:
            model_name:
            site:

        Returns:
            projections(list): of player dict
        '''
        projections = []
        cols = ['Player_Name', 'Team', 'Position', 'Salary', 'AvgPts', 'Ceiling', 'Floor']
        headers = ['player', 'team', 'position', 'salary', 'fppg', 'ceiling', 'floor']
        transform = dict(zip(cols, headers))

        # can use agent to get players, if that fails, then throw exception
        if not players:
            players = self.model(model_date, model_name, site)

            if not players:
                raise ValueError('must have projections or specify model_date')

        # correct D -> DST
        # alter projection using criteria if specify projection formula
        # leave flexible so can alter projections in R if want to
        for p in players:
            player = {transform[k]: v for k, v in p.items() if k in cols}
            if player.get('position') == 'D':
                player['position'] = 'DST'
            if projection_formula:
                player['fppg'] = alter_projection(p, ['AvgPts', 'Ceiling', 'Floor'], projection_formula, randomize)
            projections.append(player)

        if fn:
            with open(fn, 'wb') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(projections)

        return projections

    def salaries(self, seasons):
        '''
        Args:
            seasons(dict): key is int,
                           value is dict where key is week, value is datestring in mm_dd_yyyy format

        Returns:
            players(list): of player dict
        '''
        players = []
        for season, weeks in seasons.items():
            for week, datestr in weeks.items():
                model = self._s.model(datestr)
                players.append(self._p.dk_salaries(model, season, week))
                time.sleep(1)

        return [item for sublist in players for item in sublist]

    def study_optimizer(self, players, iterations=5):
        '''
        Take actual results and look at optimal lineups from past weeks
        Args:
            players(list): of list of player dicts

        Returns:
            df(DataFrame): optimizer results
        '''

        week_players = []

        for p in players:
            oppos = str(p.get('Opposing_TeamFB', '').replace('@', ''))
            pos = str(p.get('Position'))
            if pos == 'D': pos = str('DST')
            team = str(p.get('Team'))
            player_name = str(p.get('Player_Name'))
            code = str('{}_{}'.format(player_name, pos))

            week_players.append(ORToolsPlayer(proj=p.get('ActualPoints', 0), matchup=p.get('Opposing_TeamFB'), opps_team=oppos, code=code, pos=pos,
                                  name=player_name, cost=p.get('Salary'), team=team))

        return run_solver(week_players, depth=iterations, iteration_id=int(time.time()))

if __name__ == '__main__':
    import pickle

    import pandas as pd

    with open('/home/sansbacon/models.pkl', 'rb') as infile:
        models = pickle.load(infile)

    from nfl.agents.fantasylabs import FantasyLabsNFLAgent as nfla
    from nfl.parsers.fantasylabs import FantasyLabsNFLParser as nflp

    parser = nflp()
    agent = nfla(None, None)
    fixed = []
    s2016 = models.get(2016)

    for year, data in models.items():
        for week, content in data.items():
            players = parser.model(content, site='dk')
            for roster in agent.study_optimizer(players, 50):
                for player in roster.sorted_players():
                    pl = dict(player)
                    pl['iteration_id'] = roster.iteration_id
                    pl['roster_id'] = roster.roster_id
                    pl['season_year'] = year
                    pl['week'] = week
                    fixed.append(pl)

    df = pd.DataFrame(fixed)
    df.to_csv('/home/sansbacon/opt.csv', index=False)