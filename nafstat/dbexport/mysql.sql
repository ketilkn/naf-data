DROP TABLE IF EXISTS coach;
CREATE TABLE coach (
    naf_number INTEGER PRIMARY KEY,
    name varchar(25) NOT NULL,
    nation varchar(24) default "UNKNOWN"
);


DROP TABLE IF EXISTS rank;
CREATE TABLE rank (
    coach_id INTEGER,
    race_id INTEGER NOT NULL,
    elo INTEGER default 15000,
    glicko INTEGER default 15000,
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

DROP TABLE IF EXISTS `match`;
CREATE TABLE `match` (
    match_id INTEGER NOT NULL,
    tournament_id INTEGER NOT NULL,
    match_date DATE,
    timeofday TIME,
    datetime DATETIME,
    gate INTEGER,
    PRIMARY KEY(match_id, tournament_id)
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
    score INTEGER,
    PRIMARY KEY(match_id, tournament_id, coach_id)
);


DROP TABLE IF EXISTS race;
CREATE TABLE race (
    race_id INTEGER PRIMARY KEY,
    race TEXT NOT NULL,
    sh CHARACTER(2)
);

