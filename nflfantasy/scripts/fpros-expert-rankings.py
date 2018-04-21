import json
import time

from nfl.agents.fantasypros import FantasyProsNFLAgent
from nfl.utility import getdb, save_json

a = FantasyProsNFLAgent(cache_name='fpros-rankings-2017')
db = getdb()

# need something for fpros players
# want format STD for QB, DST, K
# want format PPR for RB, WR, TE
q = """
  SELECT source_player_code as pcode, source_player_position as pos  
  FROM extra_misc.player_xref 
  WHERE source = 'fantasypros' 
    AND source_player_code IS NOT NULL
    AND source_player_position IS NOT NULL 
  ORDER BY source_player_code
"""

fpros_players = db.select_dict(q)
posfmt = {'QB': 'STD', 'K': 'STD', 'DST': 'STD',
          'RB': 'PPR', 'WR': 'PPR', 'TE': 'PPR'}

rankings = []
for week in range(1,18):
    for pl in fpros_players:
        fmt = posfmt[(pl['pos'])]
        content = a._s.player_weekly_rankings(pid=pl['pcode'], 
                                           week=week, 
                                           fmt=pl['fmt'])
        rankings.append(a._p.player_weekly_rankings(content))
        time.sleep(.5)
save_json([item for sublist in rankings for item in sublist],
          'fpros-rankings-2017.json')
