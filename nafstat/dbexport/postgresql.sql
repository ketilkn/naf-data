DROP TABLE IF EXISTS coach;
CREATE TABLE coach (
    naf_number integer PRIMARY KEY,
    name varchar(25) NOT NULL,
    nation varchar(24) default 'unknown'
);


DROP TABLE IF EXISTS rank;
CREATE TABLE rank (
    coach_id INTEGER,
    race_id INTEGER NOT NULL,
    elo INTEGER default 15000,
    glicko REAL default 15000,
    PRIMARY KEY(coach_id, race_id)
);


DROP TABLE IF EXISTS tournament;
CREATE TABLE tournament (
    tournament_id INTEGER PRIMARY KEY,
    name varchar(128) NOT NULL,
    organizer varchar(128) NOT NULL,
    scoring TEXT NOT NULL,
    nation varchar(24) NOT NULL,
    start_date DATE,
    end_date DATE,
    information TEXT,
    style TEXT,
    type varchar(12),
    webpage varchar(128),
    ruleset varchar(12),
    swiss BOOLEAN,
    casualties INTEGER,
    variant varchar(24),
    city varchar(64)
);

DROP TABLE IF EXISTS game;
CREATE TABLE game (
    game_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    game_date DATE,
    timeofday TIME,
    datetime TIMESTAMP WITH TIME ZONE ,
    gate INTEGER,
    PRIMARY KEY(game_id, tournament_id)
);

DROP TABLE IF EXISTS coachgame;
DROP TYPE IF EXISTS game_result;
CREATE TYPE game_result AS ENUM('W', 'T', 'L');
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
    result game_result,
    winnings INTEGER,
    score INTEGER,
    PRIMARY KEY(tournament_id, game_id, coach_id)
);


DROP TABLE IF EXISTS race;
CREATE TABLE race (
    race_id INTEGER PRIMARY KEY,
    race VARCHAR(16) NOT NULL,
    sh CHARACTER(2)
);


