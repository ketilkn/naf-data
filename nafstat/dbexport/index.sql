CREATE INDEX IF NOT EXISTS coach_name ON coach(name);

CREATE INDEX IF NOT EXISTS rank_coach_race ON rank(coach_id, race);
CREATE INDEX IF NOT EXISTS rank_elo ON rank(elo);

CREATE INDEX IF NOT EXISTS tournament_location ON tournament(location);
CREATE INDEX IF NOT EXISTS tournament_start ON tournament(start_date);
CREATE INDEX IF NOT EXISTS tournament_end ON tournament(end_date);

CREATE INDEX IF NOT EXISTS match_home_coach ON match(home_coach);
CREATE INDEX IF NOT EXISTS match_home_race ON match(home_race);
CREATE INDEX IF NOT EXISTS match_away_coach ON match(away_coach);
CREATE INDEX IF NOT EXISTS match_away_race ON match(away_race);


