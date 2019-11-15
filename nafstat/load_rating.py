#!/usr/bin/env python
"""  Load rating (glicko) from file"""
import csv
import logging
import collections

#LOG = logging.getLogger(__name__)
LOG = logging.getLogger("nafstat")

Rating = collections.namedtuple("Rating", "coach race rating naf_number")


def ratings_to_dict(ratings, attribute="coach"):
    """ With list of Rating, return dict by attribute (coach name by default)"""
    LOG.debug("Organize ratings to dict")
    result = collections.defaultdict(list)
    for rating in ratings:
        result[getattr(rating, attribute)].append(rating)
    return result


def from_csv(filename,
             coach_column="coach", race_column="race", rating_column="curr_rating", naf_number_column="naf_number",
             delimiter=","):
    """Load csv file and yield Rank(coach race rating)"""
    LOG.debug("Reading rating from %s using %s %s %s %s", filename, coach_column, race_column, rating_column, naf_number_column)

    with open(filename) as csv_file:
        reader = csv.DictReader(csv_file, delimiter=delimiter)
        for index, row in enumerate(reader):
            try:
                if not row[naf_number_column]:
                    LOG.warning("Row #%s, %s is missing naf_number", index, row[coach_column])
                race = " ".join(map(str.capitalize, row[race_column].split(' ')))
                yield Rating(row[coach_column], race, row[rating_column], float(row[naf_number_column]))
            except Exception as ex:
                LOG.exception(ex)
                LOG.error(row)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO if "--debug" not in sys.argv else logging.DEBUG, format=log_format)
    import datetime
    import random
    LOG.info("Load rating started at %s", datetime.datetime.now().isoformat())
    import argparse

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("csv_filename")
    argument_parser.add_argument("--debug", action="store_true")

    arguments = argument_parser.parse_args()

    ratings = list(from_csv(arguments.csv_filename))
    LOG.info("Found %s ratings", len(ratings))
    LOG.info("Printing a random selection of 5")

    for c in random.choices(ratings, k=5):
        print(c)

    LOG.info("Printing coach The_Ref")
    by_coach = ratings_to_dict(ratings)
    for r in by_coach["The_Ref"]:
        print(r)

    LOG.info("Printing a random selection from Khorne")
    by_race = ratings_to_dict(ratings, attribute="race")
    for r in random.choices(by_race["Khorne"], k=5):
        print(r)


if __name__ == "__main__":
    main()

