DROP VIEW IF EXISTS all_matches;
CREATE VIEW all_matches AS
SELECT match_date as date, match.tournament_id, match.match_id, tournament.name as tournament_name,
    home.coach as home_coach, homerace.race as home_race, home.result as home_result, home.score as home_score,
    away.score as away_score, away.result as away_result, awayrace.race as away_race, away.coach as away_coach,
    tournament.casualties as "casualties?", home.bh+home.si+home.dead as home_cas, away.bh+away.si+away.dead as away_cas,
    home.race_id=away.race_id as mirror, home.tr as home_tr, away.tr as away_tr,
    variant, swiss, ruleset, style, location, coach_home.nation as home_nationality, coach_away.nation as away_nationality
FROM match
JOIN tournament ON match.tournament_id=tournament.tournament_id
JOIN coachmatch home ON match.tournament_id=home.tournament_id AND match.match_id=home.match_id AND home.hoa="H"
JOIN coachmatch away ON match.tournament_id=away.tournament_id AND match.match_id=away.match_id AND away.hoa="A"
JOIN race homerace ON home.race_id=homerace.race_id
JOIN race awayrace ON away.race_id=awayrace.race_id
LEFT JOIN coach coach_home ON home.coach=coach_home.name
LEFT JOIN coach coach_away ON away.coach=coach_away.name;


DROP VIEW IF EXISTS invert_all_matches;
CREATE view invert_all_matches AS
SELECT match_date as date, match.tournament_id, match.match_id, tournament.name as tournament_name,
    home.coach as home_coach, homerace.race as home_race, home.result as home_result, home.score as home_score,
    away.score as away_score, away.result as away_result, awayrace.race as away_race, away.coach as away_coach,
    tournament.casualties as "casualties?", home.bh+home.si+home.dead as home_cas, away.bh+away.si+away.dead as away_cas,
    home.race_id=away.race_id as mirror, home.tr as home_tr, away.tr as away_tr,
    variant, swiss, ruleset, style, location, coach_home.nation as home_nationality, coach_away.nation as away_nationality
FROM match
JOIN tournament ON match.tournament_id=tournament.tournament_id
JOIN coachmatch home ON match.tournament_id=home.tournament_id AND match.match_id=home.match_id AND home.hoa="A"
JOIN coachmatch away ON match.tournament_id=away.tournament_id AND match.match_id=away.match_id AND away.hoa="H"
JOIN race homerace ON home.race_id=homerace.race_id
JOIN race awayrace ON away.race_id=awayrace.race_id
LEFT JOIN coach coach_home ON home.coach=coach_home.name
LEFT JOIN coach coach_away ON away.coach=coach_away.name;

DROP VIEW IF EXISTS repeat_all_matches;
CREATE view repeat_all_matches AS
  SELECT * FROM all_matches
  UNION
  SELECT * FROM invert_all_matches;
