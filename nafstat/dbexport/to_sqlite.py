#!/usr/bin/env python
"""  Parse match from HTML """
import copy
import logging
import argparse
import sqlite3

from nafstat import coachlist
import nafstat.collate
LOG = logging.getLogger(__package__)


def save_tournament(tournament, connection):
    LOG.debug("Save tournament %s", tournament["tournament_id"])
    query = """
        INSERT INTO tournament 
        (tournament_id, name, organizer, scoring, start_date, end_date, information, style, type, webpage, ruleset, location, swiss, casualties, variant) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

    result = connection.execute(query, (
                               tournament["tournament_id"],
                               tournament["name"],
                               tournament["organizer"],
                               tournament["scoring"],
                               tournament["start_date"],
                               tournament["end_date"],
                               tournament["information"],
                               tournament["style"],
                               tournament["type"],
                               tournament["webpage"],
                               tournament["ruleset"],
                               tournament["location"],
                               tournament["swiss"],
                               tournament["casualties"],
                               tournament["variant"],))
    LOG.debug("Save result %s", result)
    #connection.commit()


def save_coach(coach, connection):
    LOG.debug("Save coach %s %s", coach["naf_number"], coach["naf_name"])
    query = """
        INSERT INTO coach 
                (naf_number, name, nation)
                VALUES (?, ?, ?)
            """
    result = connection.execute(query, (coach["naf_number"], coach["naf_name"],  coach["nation"]))


def save_rank(coach, ranking, connection):
    LOG.debug("Save team %s %s", coach["naf_number"], ranking["race"])
    query = """
        INSERT INTO rank 
                (coach_id, race, elo)
                VALUES (?, ?, ?)
            """
    result = connection.execute(query, (coach["naf_number"], ranking["race"],  ranking["elo"]*100))


def add_coaches(connection):
    LOG.debug("Adding all coaches")
    for c in coachlist.load_all():
        save_coach(c, connection)
        for rank in c["ranking"].values():
            save_rank(c, rank, connection)


def save_match(match, coaches, connection):
    query = """
        INSERT INTO match (
            match_id, tournament_id, match_date, timeofday, datetime,
            away_coach, away_race, away_bh, away_si, away_dead,
            away_result, away_tr, away_score, away_winnings,
            home_coach, home_race, home_bh, home_si, home_dead,
            home_result, home_tr, home_score, home_winnings,
            gate)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """

    result = connection.execute(query, (
         match["match_id"], match["tournament_id"], match["date"], match["time"], match["datetime"],
         match["away_coach"], match["away_race"], match["away_bh"], match["away_si"], match["away_dead"],
         match["away_result"], match["away_tr"], match["away_score"], match["away_winnings"],
         match["home_coach"], match["home_race"], match["home_bh"], match["home_si"], match["home_dead"],
         match["home_result"], match["home_tr"], match["home_score"], match["home_winnings"],
         match["gate"],))
    LOG.debug("Save result %s", result)


def all_tournaments(connection):
    coaches = coachlist.load_dict_by_name()
    for t in nafstat.collate.load_all():
        save_tournament(tournament=t, connection=connection)
        for m in t["matches"]:
            match = copy.copy(m)
            match["tournament_id"] = t["tournament_id"]
            match["tmid"] = "%s#%s".format(t['tournament_id'], m['match_id'].zfill(3))
            match["datetime"] = '{} {}'.format(m["date"], m["time"])
            save_match(match, coaches, connection)


def create_schema(connection, filename="nafstat/dbexport/schema.sql"):
    LOG.debug("Creating schema from %s", filename)
    connection.executescript(open(filename, "r").read())
    LOG.debug("Schema OK")


def create_index(connection, filename="nafstat/dbexport/index.sql"):
    create_schema(connection, filename)

def to_db(filename):
    LOG.info("Connection to %s", filename)
    connection = sqlite3.connect(filename)

    LOG.info("Create schema")
    create_schema(connection)

    LOG.info("Create index")
    create_index(connection)
    
    LOG.info("Add coaches")
    add_coaches(connection.cursor())
    connection.commit()

    LOG.info("Add tournaments")
    all_tournaments(connection.cursor())

    connection.commit()
    connection.close()


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("output_file")

    arguments = argument_parser.parse_args()

    if not arguments.output_file.endswith(".db"):
        sys.exit("Sure? '{}' does not end with .db".format(arguments.output_file))

    to_db(arguments.output_file)


if __name__ == "__main__":
    main()
