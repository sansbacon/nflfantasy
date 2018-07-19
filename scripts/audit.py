# auditing gamelogs
# test if season total = gamelog total

from nfl.scrapers.pfr import *
from nfl.parsers.pfr import *

season_year = 2017

auditq = """
WITH pw AS (
  SELECT source_player_id, source_player_name, week, fanduel_points
  FROM extra_fantasy.playerstats_fantasy_weekly
  WHERE season_year = {} AND source='pfr'
  ORDER BY source_player_id, week
),

weekly AS (
  SELECT 
    source_player_id, sum(fanduel_points) as weekly_sum, 
    array_agg(week) as weeks,
    array_agg(fanduel_points) as scores
  FROM pw 
  GROUP BY source_player_id
),

yearly AS (
  SELECT source_player_id, fanduel_points as yearly_sum
  FROM extra_fantasy.playerstats_fantasy_yearly
  WHERE season_year = {} AND source='pfr'
),

audit AS (
  SELECT weekly.*, yearly.yearly_sum, ROUND((weekly.weekly_sum - yearly.yearly_sum)::numeric, 2) as d
  FROM weekly 
    LEFT JOIN yearly ON weekly.source_player_id = yearly.source_player_id
)

SELECT 
  pw.source_player_id, pw.source_player_name, 
  audit.weeks, audit.scores, audit.weekly_sum, 
  audit.yearly_sum, audit.d
FROM audit
LEFT JOIN pw ON audit.source_player_id = pw.source_player_id
WHERE d <> 0;
"""

# these need to be inserts rather than updates
# the on conflict will update if the record already exists
# seems like this would be much easier using something like
# sql alchemy then trying to hard code it
iq1 = """
INSERT INTO fantasy.playerstats_weekly
(season_year, week, source, source_player_id, source_player_name,
 source_player_position, source_team_id, fanduel_points)
VALUES(%s, %s, 'pfr', %s, %s, %s, %s, %s)
ON CONFLICT (playerstats_fantasy_weekly_season_year_week_source_source_p_key) 
DO UPDATE 
SET fanduel_points = EXCLUDED.fanduel_points;
"""

# these need to be inserts rather than updates
# the on conflict will update if the record already exists
iq2 = """
INSERT INTO fantasy.playerstats_yearly
(season_year, source, source_player_id, source_player_name,
 source_player_position, source_team_id, fanduel_points)
VALUES %s
ON CONFLICT (playerstats_fantasy_weekly_season_year_week_source_source_p_key) 
DO UPDATE 
SET fanduel_points = EXCLUDED.fanduel_points;
"""


pfrs = PfrNFLScraper()
pfrp = PfrNFLParser()
cur = db.conn.cursor()
for p in db.select_dict(auditq.format(season_year)):
    pid = p['source_player_id']
    url = 'https://www.pro-football-reference.com/players/{initial}/{pid}/fantasy/{yr}'
    content = s.get(url.format(initial=pid[0], pid=pid, yr=season_year))
    weeks, tot = pfrp.fantasy_gamelogs(content)
    execute_values(cur, iq2, [(season_year, 'pfr', p['source_player_id'],
                   p['source_player_name'], p['source_team_id'], tot['fanduel_points'])])

