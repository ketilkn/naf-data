#!/usr/bin/env python
"""  Parse match from HTML """
import shutil
import copy
import logging

import csv
from tqdm import tqdm
import nafstat.coachlist
LOG = logging.getLogger(__package__)


def to_csv(coaches, output_file="all_coaches.csv"):
    copy_to = "/home/ketilkn/www/ghoulhq.com/nafdata/all_coaches.csv"
    LOG.info("Opening file %s", output_file)

    with open(output_file, 'w') as csvfile:
        LOG.info("Writing coach list to %s", output_file)
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
        for c in tqdm(coaches):
            csv_writer.writerow(c)
    LOG.debug("Finished writing %s", output_file)
    #LOG.info("Copy file to target")
    #shutil.copy(output_file, copy_to)


def all_coaches():
    for coach_race in nafstat.coachlist.load_by_race():
        yield coach_race


def do_it(filename):
    import collections
    race_counter = collections.Counter()

    LOG.info("Load coaches")
    coaches = sorted(all_coaches(), key=lambda m: m["elo"], reverse=True)
    LOG.info("Adding ranking")
    for rank, c in enumerate(coaches, 1):
        race_counter[c["race"]] += 1
        c["rank"] = rank
        c["race_rank"] = race_counter[c["race"]]
    to_csv(coaches, filename)


def run_with_arguments(args):
    do_it(filename=args.target)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    LOG.info("All matches")


if __name__ == "__main__":
    main()
