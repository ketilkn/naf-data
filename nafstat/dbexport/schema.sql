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

DROP TABLE IF EXISTS tournament_award;
CREATE TABLE tournament_award (
    tournament_id INTEGER NOT NULL,
    coach_id INTEGER,
    award_id INTEGER,
    UNIQUE (tournament_id, coach_id, award_id) ON CONFLICT REPLACE
);

DROP TABLE IF EXISTS award;
CREATE TABLE award (
    award_id INTEGER NOT NULL,
    name TEXT,
    UNIQUE (award_id) ON CONFLICT REPLACE
);

INSERT INTO award VALUES(1, 'Winner'), (2, 'Runner up'), (3, 'Most Touchdowns'), (4, 'Most Casualties'), (5, 'Stunty Cup'), (6, 'Best Painted');


DROP TABLE IF EXISTS game;
CREATE TABLE game (
    game_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    game_date TEXT,
    timeofday TEXT,
    datetime TEXT,
    gate INTEGER,
    UNIQUE(game_id, tournament_id)
);

DROP TABLE IF EXISTS coachgame;
CREATE TABLE coachgame (
    game_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    hoa CHARACTER(1) NOT NULL,
    coach_id INTEGER,
    race_id INTEGER,
    bh INTEGER,
    si INTEGER,
    dead INTEGER,
    tr INTEGER,
    result CHARACTER(1),
    winnings INTEGER,
    score INTEGER
);


DROP TABLE IF EXISTS race;
CREATE TABLE race (
    race_id INTEGER PRIMARY KEY,
    race TEXT NOT NULL,
    sh CHARACTER(2)
);

