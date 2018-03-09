#!/usr/bin/env python
"""  Parse match from HTML """
import shutil
import copy
import logging

import csv

import nafstat.coachlist
LOG = logging.getLogger(__package__)


def to_csv(coaches):
    output_file = "all_coaches.csv"
    copy_to = "/home/ketilkn/Dropbox/bloodbowl/nafdata/all_coaches.csv"
    LOG.debug("Opening file all_coaches.csv")
    with open('all_coaches.csv', 'w') as csvfile:
        columns = ["naf_number",
                   "naf_name",
                   "nation",
                   "race",
                   "elo",
                   "race_rank",
                   "rank"]
        csv_writer = csv.DictWriter(csvfile, fieldnames=columns, extrasaction='ignore', quotechar='"')
        LOG.debug("Write header")
        csv_writer.writeheader()
        tournament_name = ""
        for c in coaches:
            csv_writer.writerow(c)
    LOG.debug("Finished writing all_coaches.csv")
    LOG.info("Copy file to target")
    shutil.copy(output_file, copy_to)


def all_coaches():
    for coach_race in nafstat.coachlist.load_by_race():
        yield coach_race


def main():
    import collections
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    LOG.info("All matches")
    race_counter = collections.Counter()

    coaches = sorted(all_coaches(), key=lambda m: m["elo"], reverse=True)
    for rank, c in enumerate(coaches, 1):
        race_counter[c["race"]] += 1
        c["rank"] = rank
        c["race_rank"] = race_counter[c["race"]]
    to_csv(coaches)


if __name__ == "__main__":
    main()
