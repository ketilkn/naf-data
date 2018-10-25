DROP VIEW IF EXISTS all_matches;
CREATE VIEW all_matches AS SELECT match_date as date, match.tournament_id, match_id, tournament.name as tournament_name,
    home_coach, home_race, home_result, home_score, away_score, away_result, away_race, away_coach,
    tournament.casualties as "casualties?", home_bh+home_si+home_dead as home_cas, away_bh+away_si+away_dead as away_cas,
    home_race=away_race as mirror, home_tr, away_tr,
    variant, swiss, ruleset, style, location, coach_home.nation as home_nationality, coach_away.nation as away_nationality
FROM match
JOIN tournament ON match.tournament_id=tournament.tournament_id
LEFT JOIN coach coach_home ON match.home_coach=coach_home.name
LEFT JOIN coach coach_away ON match.away_coach=coach_away.name;


DROP VIEW IF EXISTS invert_match;
CREATE view invert_match AS
  SELECT match_id, tournament_id, match_date, timeofday, datetime, 
   home_coach as away_coach, home_race as away_race, home_bh as away_bh, home_si as away_si, home_dead as away_dead, home_tr as away_tr, home_result as away_result, home_score as away_score,
   away_score as home_score, away_result as home_result, away_coach as home_coach, away_race as home_race, away_bh as home_bh, away_si as home_si, away_dead as home_dead, away_tr as home_tr,
   home_winnings as away_winning, away_winnings as home_winning,
   gate
  FROM match;

DROP VIEW IF EXISTS repeat_match;
CREATE view repeat_match AS
  SELECT * FROM match
  UNION
  SELECT * FROM invert_match;
