def preprocess_fantasylabs(players):
    # id,  first_name, last_name, positions, team, salary, fppg, is_injured=False):
    pydfs_players = []
    for p in players:
        parts = p.get('Player_Name', '').split(' ')
        if parts and len(parts) == 2:
            first_name, last_name = parts
        else:
            first_name = p.get('Player_Name')
            last_name = ''
        positions = [p.get('Position')]
        salary = float(p.get('Salary', 0))
        fppg = float(p.get('AvgPts', 0))
        pydfs_players.append(Player('', first_name, last_name, positions, '', salary, fppg))

    return pydfs_players

if __name__ == '__main__':

    import json
    import pandas as pd
    from pydfs_lineup_optimizer import LineupOptimizer, DraftKingsFootballSettings, Player

    from nfl.scrapers.fantasylabs import FantasyLabsNFLScraper
    from nfl.parsers.fantasylabs import FantasyLabsNFLParser


    s = FantasyLabsNFLScraper()
    p = FantasyLabsNFLParser()
    optimizer = LineupOptimizer(DraftKingsFootballSettings)

    # get fl data
    with open('/home/sansbacon/w13_levitan_model.json', 'r') as infile:
        model = json.load(infile)

    players = {player.get('PlayerId'): player for player in p.model(model, 'dk')}.values()
    for idx, p in enumerate(players):
        if p.get('Position') == 'D': players[idx]['Position'] = 'DST'
    df = pd.DataFrame(players)

    # ['Position', 'Name', 'Salary', 'GameInfo', 'AvgPointsPerGame', 'teamAbbrev']
    df['Name'] = df['Player_Name']
    df['AvgPointsPerGame'] = df['AvgPts']
    df['GameInfo'] = df['Opposing_TeamFB']
    df['teamAbbrev'] = df['Team']
    df = df.sort('Salary', ascending=False)
    cols = ['Position', 'Name', 'Salary', 'GameInfo', 'AvgPointsPerGame', 'teamAbbrev']
    df.to_csv('/home/sansbacon/1.csv', index=False, columns=cols)
    optimizer.load_players_from_CSV('/home/sansbacon/1.csv')

    for lineup in optimizer.optimize(n=5):
        print lineup
