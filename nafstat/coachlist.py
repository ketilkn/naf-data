#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging
import os

import nafstat.file_loader
import nafparser.coach


LOG = logging.getLogger(__package__)


def load_dict_by_name():
    coaches = {}
    for c in load_all():
        coaches[c["naf_name"]] = c
    return coaches


def load_dict_by_id():
    coaches = {}
    for c in load_all():
        coaches[c["naf_number"]] = c
    return coaches


def load_invalid():
    for coach in load_all():
        for index, race in enumerate(coach["ranking"].values()):
            if not float(race["elo"]):
                yield coach


def load_all():
    LOG.debug("loading all coaches")

    for filename in os.listdir("data/coach/"):
        if not filename.startswith(".") and filename.endswith(".html"):
            coach = nafstat.file_loader.load_cached(nafparser.coach.parse_html, os.path.join("data/coach", filename))
            if coach:
                yield coach


def load_by_race():
    LOG.debug("loading all coaches")

    for filename in os.listdir("data/coach/"):
        if not filename.startswith(".") and filename.endswith(".html"):
            coach = nafstat.file_loader.load_cached(nafparser.coach.parse_html, os.path.join("data/coach", filename))
            if coach and coach["ranking"]:
                for index, race in enumerate(coach["ranking"].values()):
                    if not float(race["elo"]):
                        LOG.warning("%s None float elo %s", coach["naf_name"], race)
                    yield {"naf_number": coach["naf_number"],
                           "naf_name": coach["naf_name"],
                           "nation": coach["nation"],
                           "race": race["race"],
                           "elo": race["elo"],
                           "match_count": race["matches"]}


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.ERROR, format=log_format)

    do_print = False if "--no-print" in sys.argv else True
    if not do_print:
        del(sys.argv[sys.argv.index("--no-print")])

    #coaches = load_invalid()
    #coaches = load_by_race()
    coaches = load_all()
    coach_count = 0
    for index, coach in enumerate(coaches):
        if coach:
            coach_count = coach_count + 1
        if do_print:
            print(coach)
        if not index % 50:
            print("Progress ", index)

    print("coach_count {}".format(coach_count))


if __name__ == "__main__":
    main()
