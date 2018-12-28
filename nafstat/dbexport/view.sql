DROP VIEW IF EXISTS all_matches;
CREATE VIEW all_matches AS SELECT match_date as date, match.tournament_id, match.match_id, tournament.name as tournament_name,
    home.coach as home_coach, home.race as home_race, home.result as home_result, home.score as home_score,
    away.score as away_score, away.result as away_result, away.race as away_race, away.coach as away_coach,
    tournament.casualties as "casualties?", home.bh+home.si+home.dead as home_cas, away.bh+away.si+away.dead as away_cas,
    home.race=away.race as mirror, home.tr as home_tr, away.tr as away_tr,
    variant, swiss, ruleset, style, location, coach_home.nation as home_nationality, coach_away.nation as away_nationality
FROM match
JOIN tournament ON match.tournament_id=tournament.tournament_id
JOIN coachmatch home ON match.tournament_id=home.tournament_id AND match.match_id=home.match_id AND home.hoa="H"
JOIN coachmatch away ON match.tournament_id=away.tournament_id AND match.match_id=away.match_id AND away.hoa="A"
LEFT JOIN coach coach_home ON home.coach=coach_home.name
LEFT JOIN coach coach_away ON away.coach=coach_away.name;


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
