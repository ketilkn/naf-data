DROP TABLE IF EXISTS coach;
CREATE TABLE coach (
    naf_number INTEGER PRIMARY KEY,
    name TEXT collate nocase NOT NULL,
    nation TEXT default "UNKNOWN",
    UNIQUE(name) ON CONFLICT REPLACE
);


DROP TABLE IF EXISTS rank;
CREATE TABLE rank (
    coach_id INTEGER,
    race_id INTEGER NOT NULL,
    elo INTEGER default 15000,
    glicko INTEGER default 15000,
    UNIQUE (coach_id, race_id) ON CONFLICT REPLACE

);


DROP TABLE IF EXISTS tournament;
CREATE TABLE tournament (
    tournament_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    organizer TEXT NOT NULL,
    scoring TEXT NOT NULL,
    nation TEXT NOT NULL,
    start_date TEXT,
    end_date TEXT,
    information TEXT,
    style TEXT,
    type TEXT,
    webpage TEXT,
    ruleset TEXT,
    swiss BOOLEAN,
    casualties INTEGER,
    variant TEXT,
    city TEXT
);

DROP TABLE IF EXISTS match;
CREATE TABLE match (
    match_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    match_date TEXT,
    timeofday TEXT,
    datetime TEXT,
    gate INTEGER,
    UNIQUE(match_id, tournament_id)
);

DROP TABLE IF EXISTS coachmatch;
CREATE TABLE coachmatch (
    match_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    hoa CHARACTER(1) NOT NULL,
    coach_id INTEGER,
    race_id INTEGER,
    bh INTEGER,
    si INTEGER,
    dead INTEGER,
    tr INTEGER,
    result INTEGER,
    winnings INTEGER,
    score INTEGER
);


DROP TABLE IF EXISTS race;
CREATE TABLE race (
    race_id INTEGER PRIMARY KEY,
    race TEXT NOT NULL,
    sh CHARACTER(2)
);

