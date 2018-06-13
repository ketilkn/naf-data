DROP TABLE IF EXISTS naf_coach;
CREATE TABLE naf_coach (
    naf_number INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    nation TEXT default "UNKNOWN"
);

DROP TABLE IF EXISTS naf_team;
CREATE TABLE naf_team (
    coach_id INTEGER,
    race TEXT NOT NULL,
    elo INTEGER default 150,
    UNIQUE (coach_id, race) ON CONFLICT REPLACE

);

DROP TABLE IF EXISTS naf_tournament;
CREATE TABLE naf_tournament (
    tournament_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    organizer TEXT NOT NULL,
    scoring TEXT NOT NULL,
    location TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    information TEXT,
    style TEXT,
    type TEXT,
    webpage TEXT,
    ruleset TEXT,
    swiss BOOLEAN,
    variant TEXT
);

DROP TABLE IF EXISTS naf_match;
CREATE TABLE naf_match (
    match_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    match_date INTEGER,
    timeofday TEXT,
    datetime TEXT,
    away_teamid INTEGER,
    away_coach TEXT,
    away_race TEXT,
    away_bh INTEGER,
    away_si INTEGER,
    away_dead INTEGER,
    away_result INTEGER,
    away_tr INTEGER,
    away_score INTEGER,
    away_winnings INTEGER,
    home_teamid INTEGER,
    home_coach TEXT,
    home_race TEXT,
    home_bh INTEGER,
    home_dead INTEGER,
    home_result TEXT,
    home_score INTEGER,
    home_si INTEGER,
    home_tr INTEGER,
    home_winnings INTEGER,
    gate INTEGER,
    UNIQUE(match_id, tournament_id)
);
