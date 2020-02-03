#!/usr/bin/env python
"""  Parse match from HTML """
import copy
import logging
import argparse
import sqlite3
from tqdm import tqdm
from nafstat import coachlist, tournamentlist
import nafstat.collate
import nafstat.load_rating
from nafstat import races
from nafstat.awards import AWARDS

LOG = logging.getLogger(__package__)

INSERT_TOURNAMENT = """ INSERT INTO tournament 
        (tournament_id, name, organizer, scoring, start_date, end_date, information, style, type, webpage, ruleset, nation, swiss, casualties, variant, city) 
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?)"""

INSERT_COACH = """ INSERT INTO coach 
                (naf_number, name, nation)
                VALUES (?, ?, ?) """

INSERT_RANK = """ INSERT INTO rank 
                (coach_id, race_id, elo)
                VALUES (?, ?, ?)
            """
INSERT_RACE = """ INSERT INTO race (race_id, race, sh) VALUES(?, ?, ?)"""


INSERT_GLICKO = """ INSERT INTO rank (glicko, coach_id, race_id) VALUES(?,?,?) """
UPDATE_GLICKO = """ UPDATE rank SET glicko = ? WHERE coach_id=? AND race_id=? """

INSERT_GAME = """ INSERT INTO game (
            game_id, tournament_id, game_date, timeofday, datetime, gate)
            values(?,?,?,?,?,?) """


INSERT_COACHGAME = """ INSERT INTO coachgame (
            game_id, tournament_id, hoa,
            coach_id, race_id, bh, si, dead, result, tr, score, winnings)
            values(?,?,?, ?,?,?,?,?,?,?,?,?) """


def insert_tournament(tournament, connection, attribute="?"):
    LOG.debug("Save tournament %s", tournament["tournament_id"])

    cursor = connection.cursor()
    result = cursor.execute(INSERT_TOURNAMENT.replace("?", attribute), (
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


def insert_award(award, connection):
    INSERT_AWARD = """
        INSERT INTO award(award_id, name) VALUES(?, ?)
    """
    award_id = len(AWARDS.keys()) + 1
    AWARDS[award_id] = award
    LOG.debug('Creating award %s %s', award_id, award)
    cursor = connection.cursor()

    cursor.execute(INSERT_AWARD, (award_id, award))
    connection.commit()
    return award_id


def lookup_award(award, connection):
    if award.lower() not in AWARDS.inverse:
        return insert_award(award, connection)
    return AWARDS.inverse[award.lower()]


def insert_tournament_awards(tournament_id, award, awardee, coaches, connection, attribute="?"):
    INSERT_TOURNAMENT_AWARD = """
        INSERT INTO  tournament_award (tournament_id, award_id, coach_id) VALUES(?, ?, ?)
    """

    cursor = connection.cursor()
    if awardee and awardee not in coaches:
        LOG.warning('Coach %s in tournament %s not found', awardee, tournament_id)
    elif awardee:
        award_id = lookup_award(award, connection)
        coach_id = coaches[awardee]['naf_number']
        result = cursor.execute(INSERT_TOURNAMENT_AWARD.replace("?", attribute), (tournament_id, award_id, coach_id))


def save_tournament_awards(tournament, coaches, connection, attribute="?"):
    LOG.debug("Save tournament %s awards", tournament["tournament_id"])

    tournament_id = tournament['tournament_id']
    for award, awardee in tournament['awards'].items():
        insert_tournament_awards(tournament_id, award, awardee, coaches, connection)
    for award, awardee in tournament['other_awards'].items():
        insert_tournament_awards(tournament_id, award, awardee, coaches, connection)


def insert_coach(coach, cursor, attribute="?"):
    LOG.debug("Save coach %s %s", coach["naf_number"], coach["naf_name"])
    return cursor.execute(INSERT_COACH.replace("?", attribute), (coach["naf_number"], coach["naf_name"],  coach["nation"]))


def save_rank(coach, ranking, cursor, attribute="?"):
    LOG.debug("Save team %s %s", coach["naf_number"], ranking["race"])
    race_id = next(race.race_id for race in races.INDEX if race.race == ranking["race"])
    return cursor.execute(INSERT_RANK.replace("?", attribute), (coach["naf_number"], race_id,  ranking["elo"]*100))


def save_race(race: races.Race, cursor, attribute="?"):
    LOG.debug("Saving %s %s", race.race_id, race.race)
    return cursor.execute(INSERT_RACE.replace("?", attribute), (race.race_id, race.race, race.sh))


def add_races(connection, attribute="?"):
    LOG.debug("Adding all races")
    cursor = connection.cursor()
    for race_id, race in enumerate(races.INDEX):
        save_race(race, cursor, attribute)
    connection.commit()


def update_coach_glicko(connection, coach_rating, attribute="?"):
    LOG.debug("Save coach rating %s", coach_rating)
    cursor = connection.cursor()

    for race_rating in coach_rating:
<<<<<<< HEAD
        try:
            race_id = next(race.race_id for race in races.INDEX if race.race == race_rating.race)
            cursor.execute(UPDATE_GLICKO.replace("?", attribute), (race_rating.rating, race_rating.naf_number, race_id))
            if cursor.rowcount != 1:
                LOG.warning("Updated %s rows for %s", cursor.rowcount, race_rating)
                LOG.info("Try insert instead")
                cursor.execute(INSERT_GLICKO.replace("?", attribute), (race_rating.rating, race_rating.naf_number, race_id))
        except Exception as ex:
            LOG.error(race_rating)
            LOG.exception(ex)


def add_glicko(connection, attribute="?"):
    LOG.debug("Adding all glicko ratings")

    rating_file = "/srv/www/ghoulhq.com/public/nafdata/export/glicko-by-race.csv"
=======
        race_id = next(race.race_id for race in races.INDEX if race.race == race_rating.race)
        cursor.execute(UPDATE_GLICKO.replace("?", attribute), (race_rating.rating, race_rating.naf_number, race_id))
        if cursor.rowcount != 1:
            LOG.debug("Updated %s rows for %s", cursor.rowcount, race_rating)
            LOG.debug("Try insert instead")
            cursor.execute(INSERT_GLICKO.replace("?", attribute), (race_rating.rating, race_rating.naf_number, race_id))


def add_glicko(connection, rating_file="../NAF/output/player_ranks.csv", attribute="?"):
>>>>>>> adb6053ad126f405f19d915c17f05c47e82cd6a2
    LOG.info("Loading ratings from file %s", rating_file)
    try:
        ranking = nafstat.load_rating.ratings_to_dict(nafstat.load_rating.from_csv(rating_file))
        for k, r in ranking.items():
            update_coach_glicko(connection, r, attribute)
    except FileNotFoundError:
        LOG.warning("Rating file %s not found. Skipping.", rating_file)


def add_coaches(connection, attribute="?"):
    LOG.debug("Adding all coaches")
    coaches = list(coachlist.load_all())

    for c in tqdm(coaches):
        cursor = connection.cursor()
        insert_coach(c, cursor, attribute)
        for rank in c["ranking"].values():
            save_rank(c, rank, cursor, attribute)


def insert_coachmatch(match, home_or_away, coaches, connection, attribute="?"):
    LOG.debug("save_coachmatch %s %s", match["match_id"], home_or_away)
    if not match[home_or_away+"_coach"] in coaches:
        LOG.warning("{} coach {} not in coaches found in match {}-{}".format(home_or_away, match[home_or_away+"_coach"], match["tournament_id"], match["match_id"]))

    race_id = next(race.race_id for race in races.INDEX if race.race == match[home_or_away+"_race"])
    coach_id = coaches[match[home_or_away+"_coach"]]["naf_number"] if match[home_or_away+"_coach"] in coaches else "-1"

    cursor = connection.cursor() if "cursor" in dir(connection) else connection
    result = cursor.execute(INSERT_COACHGAME.replace("?", attribute), (
        match["match_id"],  match["tournament_id"], "A" if home_or_away == 'away' else "H",
        coach_id, race_id,
        match[home_or_away+"_bh"], match[home_or_away+"_si"], match[home_or_away+"_dead"],
        match[home_or_away+"_result"], match[home_or_away+"_tr"], match[home_or_away+"_score"], match[home_or_away+"_winnings"]))
    return result


def insert_match(match, coaches, connection, attribute):
    cursor = connection.cursor()
    result = cursor.execute(INSERT_GAME.replace("?", attribute), (
         match["match_id"], match["tournament_id"], match["date"], match["time"], match["datetime"], match["gate"],))

    LOG.debug("Save result %s", result)


def all_tournaments(connection, attribute="?"):
    coaches = coachlist.load_dict_by_name()
    for t in tqdm(nafstat.collate.load_all(), total=len(tournamentlist.list_tournaments())):
        insert_tournament(tournament=t, connection=connection, attribute=attribute)
        save_tournament_awards(tournament=t, coaches=coaches, connection=connection, attribute=attribute)
        for m in t["matches"]:
            match = copy.copy(m)
            match["tournament_id"] = t["tournament_id"]
            match["tmid"] = "%s#%s".format(t['tournament_id'], m['match_id'].zfill(3))
            match["datetime"] = '{} {}'.format(m["date"], m["time"])
            match["tmid"] = "{}#{}".format(t['tournament_id'], m['match_id'].zfill(3))
            match["datetime"] = '{} {}'.format(m["date"], m["time"])

            if match["home_coach"] == match["away_coach"]:
                LOG.warning("%s was playing themselves at %s game %s %s",
                            match["home_coach"], match["tournament_id"], match["match_id"], match["datetime"])
            else:
                insert_match(match, coaches, connection, attribute)
                insert_coachmatch(match, "home", coaches, connection, attribute)
                insert_coachmatch(match, "away", coaches, connection, attribute)


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

    LOG.info("Add glicko")
    add_glicko(connection, rating_file='data/glicko-by-race.csv')
    add_glicko(connection, rating_file='data/glicko.csv')
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
