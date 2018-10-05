# DK - start of week plan:
# dkweek.py

import logging

import arrow
from nflmisc.browser import BrowserScraper
from nfl.seasons import current_season_year, season_week
from nfl.utility import getdb


def dkgames(scraper, draft_group, main_slate=True, slate_name='Sun 1:00PM'):
    # games
    # description, gameId, awayTeamId, homeTeamId, startDate
    # t = arrow.get(game['startDate'])
    # dt = t.datetime
    dgurl = 'https://api.draftkings.com/draftgroups/v1/{}?format=json'
    content = scraper.get_json(dgurl.format(draft_group))
    games = []

    for item in content['draftGroup']['games']:
        t = arrow.get(item['startDate'])
        sw = season_week(t.datetime.date())
        away, home = item.get('description').split(' @ ')
        games.append({'season_year': sw['season'], 'week': sw['week'],
                      'game_date': t.datetime,
                      'source_game_id': item['gameId'], 'source_home_team_code': home,
                      'source_away_team_code': away, 'main_slate': main_slate,
                      'slate_name': slate_name, 'slate_size': len(games)})
    return games


def dkcontests(scraper, slate_name='Sun 1:00PM', game_type='Classic'):
    '''
    
    Args:
        scraper: 
        slate_name:

    Returns:

    '''
    contest_page = scraper.get_json('https://www.draftkings.com/lobby/getcontests?sport=NFL')
    if not contest_page:
        raise ValueError('scraper could not get contest page')

    for contest in contest_page.get('Contests'):
        if contest.get('sdstring') == slate_name and contest.get('gameType') == game_type:
            return contest.get('dg')

    return None


def dkplayers(scraper, draft_group):
    '''

    Args:
        scraper: 
        slate_name:

    Returns:

    '''
    # draftableId: id used when uploading lineups
    # playerId: is stable ID, that is for the player_xref table
    # displayName, playerId, teamAbbreviation, position, salary
    # draftStatAttributes: sortValue --> [0] ppg  [1] rank
    players = []
    draftables_url = 'https://api.draftkings.com/draftgroups/v1/draftgroups/{}/draftables?format=json'
    content = scraper.get_json(draftables_url.format(draft_group))
    for item in {p.get('draftableId'): p for p in content['draftables']}.values():

        # get year, week of the competition
        comp = item['competition']
        t = arrow.get(comp['startTime'])
        sw = season_week(t.datetime.date())

        # competition has home & away codes
        away = comp['nameDisplay'][0]['value']
        home = comp['nameDisplay'][2]['value']
        if item['teamAbbreviation'] == away:
            player_team = away
            opp = home
        elif item['teamAbbreviation'] == home:
            player_team = home
            opp = away
        else:
            raise ValueError('no home/away: {}'.format(comp))

        # competition has game_id
        game_id = comp['competitionId']

        # draftStatAttributes has dvp & player fppg
        dsa = item['draftStatAttributes']
        try:
            fppg = float(dsa[0]['sortValue'])
        except:
            fppg = None
        try:
            dvp = float(dsa[1]['sortValue'])
        except:
            dvp = None

        # now create the player
        players.append({'season_year': sw['season'], 'week': sw['week'], 'draft_group': draft_group,
                      'source_game_id': game_id,
                      'source_player_id': item['playerId'], 'source_draftable_id': item['draftableId'],
                      'source_player_name': item['displayName'], 'source_player_position': item['position'],
                      'source_team_code': player_team, 'source_opp_code': opp,
                      'salary': int(item['salary']), 'ppg': fppg,'opp_rating': dvp})

    return players


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    scraper = BrowserScraper()
    db = getdb()
    draft_group = dkcontests(scraper)

    # insert games into database
    #for g in dkgames(scraper, draft_group):
    #    db._insert_dict(g, 'extra_fantasy.dk_weekly_games')

    # insert players into database
    for p in dkplayers(scraper, draft_group):
        db._insert_dict(p, 'extra_fantasy.dk_weekly_players')

    # now update nflcom_ids (using player_xref table)
    sql = """
        UPDATE extra_fantasy.dk_weekly_players
        SET nflcom_player_id = sq.nflcom_player_id
        FROM (
            SELECT * FROM extra_misc.player_xref WHERE source = 'dk'
        ) sq
        WHERE extra_fantasy.dk_weekly_players.source_player_id = sq.source_player_id::int
        AND extra_fantasy.dk_weekly_players.nflcom_player_id IS NULL;
    """
    db.execute(sql)