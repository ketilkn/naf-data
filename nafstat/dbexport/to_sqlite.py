#!/usr/bin/env python
"""  Parse match from HTML """
import copy
import logging
import argparse
import sqlite3

from tqdm import tqdm
from nafstat import coachlist
from nafstat.tournament import tournamentlist
import nafstat.collate
from nafstat import races

LOG = logging.getLogger(__package__)


def save_tournament(tournament, connection):
    LOG.debug("Save tournament %s", tournament["tournament_id"])
    query = """
        INSERT INTO tournament 
        (tournament_id, name, organizer, scoring, start_date, end_date, information, style, type, webpage, ruleset, nation, swiss, casualties, variant, city) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?)"""

    cursor = connection.cursor()
    result = cursor.execute(query, (
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
                               tournament["nation"] if "nation" in tournament else tournament["location"],
                               tournament["swiss"],
                               tournament["casualties"],
                               tournament["variant"],
                               tournament["city"] if "city" in tournament else "",
                               ))
    LOG.debug("Save result %s", result)
    #connection.commit()


def save_coach(coach, cursor):
    LOG.debug("Save coach %s %s", coach["naf_number"], coach["naf_name"])
    query = """
        INSERT INTO coach 
                (naf_number, name, nation)
                VALUES (?, ?, ?)
            """
    return cursor.execute(query, (coach["naf_number"], coach["naf_name"],  coach["nation"]))


def save_rank(coach, ranking, cursor):
    LOG.debug("Save team %s %s", coach["naf_number"], ranking["race"])
    query = """
        INSERT INTO rank 
                (coach_id, race_id, elo)
                VALUES (?, ?, ?)
            """
    race_id = next(race.race_id for race in races.INDEX if race.race == ranking["race"])
    return cursor.execute(query, (coach["naf_number"], race_id,  ranking["elo"]*100))


def save_race(race: races.Race, cursor):
    LOG.debug("Saving %s %s", race.race_id, race.race)
    query = """ INSERT INTO race (race_id, race, sh) VALUES(?, ?, ?)"""
    return cursor.execute(query, (race.race_id, race.race, race.sh))


def add_races(connection):
    LOG.debug("Adding all races")
    cursor = connection.cursor()
    for race_id, race in enumerate(races.INDEX):
        save_race(race, cursor)


def add_coaches(connection):
    LOG.debug("Adding all coaches")
    coaches = list(coachlist.load_all())
    for c in tqdm(coaches):
        cursor = connection.cursor()
        save_coach(c, cursor)
        for rank in c["ranking"].values():
            save_rank(c, rank, cursor)


def save_coachmatch(match, home_or_away, coaches, cursor):
    LOG.debug("save_coachmatch %s %s", match["match_id"], home_or_away)
    if not match[home_or_away+"_coach"] in coaches:
        LOG.warning("{} coach {} not in coaches found in match {}-{}".format(home_or_away, match[home_or_away+"_coach"], match["tournament_id"], match["match_id"]))

    race_id = next(race.race_id for race in races.INDEX if race.race == match[home_or_away+"_race"])
    coach_id = coaches[match[home_or_away+"_coach"]]["naf_number"] if match[home_or_away+"_coach"] in coaches else "-1"
    query = """
        INSERT INTO coachmatch (
            match_id, tournament_id, hoa,
            coach_id, race_id, bh, si, dead, result, tr, score, winnings)
            values(?,?,?, ?,?,?,?,?,?,?,?,?)
    """

    result = cursor.execute(query, (
        match["match_id"],  match["tournament_id"], "A" if home_or_away == 'away' else "H",
        coach_id, race_id,
        match[home_or_away+"_bh"], match[home_or_away+"_si"], match[home_or_away+"_dead"],
        match[home_or_away+"_result"], match[home_or_away+"_tr"], match[home_or_away+"_score"], match[home_or_away+"_winnings"]))
    return result


def save_match(match, coaches, connection):
    query = """
        INSERT INTO match (
            match_id, tournament_id, match_date, timeofday, datetime, gate)
            values(?,?,?,?,?,?)
    """

    cursor = connection.cursor()
    result = cursor.execute(query, (
         match["match_id"], match["tournament_id"], match["date"], match["time"], match["datetime"], match["gate"],))

    save_coachmatch(match, "home", coaches, cursor)
    save_coachmatch(match, "away", coaches, cursor)

    LOG.debug("Save result %s", result)


def all_tournaments(connection):
    coaches = coachlist.load_dict_by_name()
    for t in tqdm(nafstat.collate.load_all(), total=len(tournamentlist.list_tournaments())):
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


def create_view(connection, filename="nafstat/dbexport/view.sql"):
    create_schema(connection, filename)


def create_index(connection, filename="nafstat/dbexport/index.sql"):
    create_schema(connection, filename)


def to_db(filename):
    LOG.info("Connection to %s", filename)
    connection = sqlite3.connect(filename)

    LOG.info("Create schema")
    create_schema(connection)

    LOG.info("Skipping index")
    #create_index(connection)

    LOG.info("Create view")
    create_view(connection)

    LOG.info("Add races")
    add_races(connection)

    LOG.info("Add coaches")
    add_coaches(connection)
    connection.commit()

    LOG.info("Add tournaments")
    all_tournaments(connection)

    connection.commit()
    connection.close()


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO if "--debug" not in sys.argv else logging.DEBUG, format=log_format)
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("output_file")

    arguments = argument_parser.parse_args()

    if not arguments.output_file.endswith(".db"):
        sys.exit("Sure? '{}' does not end with .db".format(arguments.output_file))

    to_db(arguments.output_file)


if __name__ == "__main__":
    main()
