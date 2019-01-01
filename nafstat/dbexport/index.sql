CREATE INDEX IF NOT EXISTS coach_name ON coach(name);

CREATE INDEX IF NOT EXISTS rank_coach_race ON rank(coach_id, race);
CREATE INDEX IF NOT EXISTS rank_elo ON rank(elo);

CREATE INDEX IF NOT EXISTS tournament_location ON tournament(location);
CREATE INDEX IF NOT EXISTS tournament_start ON tournament(start_date);
CREATE INDEX IF NOT EXISTS tournament_end ON tournament(end_date);

CREATE INDEX IF NOT EXISTS coachmatch_coach ON coachmatch(coach);
CREATE INDEX IF NOT EXISTS coachmatch_race ON coachmatch(race);
CREATE INDEX IF NOT EXISTS match_date_index ON match(match_date);
CREATE INDEX IF NOT EXISTS coachmatch_hoa ON coachmatch(hoa);

