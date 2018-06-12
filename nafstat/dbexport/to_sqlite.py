#!/usr/bin/env python
"""  Parse match from HTML """
import copy
import logging
import argparse
import sqlite3

import nafstat.collate
LOG = logging.getLogger(__package__)


def switch_home_away(m):
    row = {}
    for key, value in m.items():
        if key.startswith("home_"):
            row[key.replace("home_", "away_")] = value
        elif key.startswith("away_"):
            row[key.replace("away_", "home_")] = value
        else:
            row[key] = value
    row["repeated_match"] = 1
    return row


def write_match(csv_writer, m):
    LOG.debug("Write match %s %s %s %s-%s %s %s",
            {m['tournament_name']}, {m['home_coach']}, {m['home_race']}, {m['home_score']}, {m['away_score']}, {m['away_race']}, {m['away_coach']})
    csv_writer.writerow(m)


def to_csv(matches, output_file = "all_matches.csv", repeat_matches = False):
    LOG.debug("Opening %s", output_file)
    with open(output_file, 'w') as csvfile:
        columns = ["date",
                   "tournament_id",
                   "match_id",
                   "tournament_name",
                   "home_coach",
                   "home_race",
                   "home_result",
                   "home_score",
                   "away_score",
                   "away_result",
                   "away_race",
                   "away_coach",
                   "casualties?",
                   "home_cas",
                   "away_cas",
                   "mirror",
                   "home_tr",
                   "away_tr",
                   "variant",
                   "swiss",
                   "ruleset",
                   "style",
                   "location",
                   "home_nationality",
                   "away_nationality"]
        if repeat_matches:
            columns.append("repeated_match")

        csv_writer = csv.DictWriter(csvfile, fieldnames=columns, extrasaction='ignore', quotechar='"')
        LOG.debug("Write header")
        csv_writer.writeheader()
        tournament_name = ""
        for m in matches:
            write_match(csv_writer, m)
            if repeat_matches:
                write_match(csv_writer, switch_home_away(m))

            if m["tournament_name"] != tournament_name:
                LOG.info("Writing tournament %s", m["tournament_name"])
                tournament_name = m["tournament_name"]

    LOG.debug("Finished writing %s", output_file)
    LOG.info("Copy file to target")


def save_tournament(tournament, connection):
    LOG.info("Save tournament %s", tournament["tournament_id"])
    query = """
        INSERT INTO naf_tournament 
        (tournament_id, name, organizer, scoring, start_date, end_date, information, style, type, webpage, ruleset, location, swiss, variant) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

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
                               tournament["variant"],))
    LOG.info("Save result %s", result)
    #connection.commit()


def save_match(match, connection):
    query = """
        INSERT INTO naf_match (
            match_id, tournament_id, match_date, timeofday, datetime,
            away_coach_id, away_bh, away_si, away_dead,
            away_result, away_tr, away_score, away_winnings,
            home_coach_id, home_bh, home_si, home_dead,
            home_result, home_tr, home_score, home_winnings,
            gate)
            values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """
    result = connection.execute(query, (
         match["match_id"], match["tournament_id"], match["date"], match["time"], match["datetime"],
         0, match["away_bh"], match["away_si"], match["away_dead"],
         match["away_result"], match["away_tr"], match["away_score"], match["away_winnings"],
         0, match["home_bh"], match["home_si"], match["home_dead"],
         match["home_result"], match["home_tr"], match["home_score"], match["home_winnings"],
         match["gate"],))
    LOG.info("Save result %s", result)


def all_matches(connection):
    for t in nafstat.collate.load_all():
        save_tournament(tournament=t, connection=connection)
        for m in t["matches"]:
            match = copy.copy(m)
            match["tournament_id"] = t["tournament_id"]
            match["tmid"] = "%s#%s".format(t['tournament_id'], m['match_id'].zfill(3))
            match["datetime"] = '%s %s'.format(m["date"], m["time"])
            save_match(match, connection)


def create_schema(connection, filename="nafstat/dbexport/schema.sql"):
    LOG.info("Creating schema from %s", filename)
    connection.executescript(open(filename, "r").read())
    LOG.debug("Schema OK")


def to_db(filename):
    LOG.info("Connection to %s", filename)
    connection = sqlite3.connect(filename)
    LOG.info("Create schema")
    create_schema(connection)
    LOG.info("Add data")
    all_matches(connection.cursor())
    connection.commit()
    connection.close()


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    LOG.info("All matches")
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("output_file")

    arguments = argument_parser.parse_args()

    if not arguments.output_file.endswith(".db"):
        sys.exit("Sure? '{}' does not end with .db".format(arguments.output_file))

    to_db(arguments.output_file)
    #to_csv(sorted(all_matches(), key=lambda m: m["order"], reverse=True),
           ##arguments.output_file,
           #repeat_matches=arguments.repeat_matches)


if __name__ == "__main__":
    main()
