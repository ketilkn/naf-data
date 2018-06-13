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
