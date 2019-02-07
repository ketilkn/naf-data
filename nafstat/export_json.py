#!/usr/bin/env python
""" Export data to sqlite """
import datetime
import argparse
import logging.config
import nafstat.collate
import nafstat.coachlist

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=False)
LOG = logging.getLogger(__name__)


def filter_match(match):
    match.pop("home_nationality", None)
    match.pop("away_nationality", None)
    match.pop("home_team", None)
    match.pop("away_team", None)
    match.pop("home_coachid", None)
    match.pop("away_coachid", None)
    match.pop("home_teamid", None)
    match.pop("away_teamid", None)
    match.pop("home_cas")
    match.pop("away_cas")
    match.pop("variant")
    match.pop("home_result")
    match.pop("away_result")
    match.pop("home_winnings")
    match.pop("away_winnings")
    return match


def filter_tournament(tournament):
    for match in tournament["matches"]:
        filter_match(match)
    tournament.pop("email", None)
    if tournament["ruleset"] == "unknown":
        tournament["ruleset"] = ""
    return tournament


def filter_data(data):
    for tournament in data:
        yield filter_tournament(tournament)


def load_data(coach_list):
    if coach_list:
        return nafstat.coachlist.load_dict_by_name()
    else:
        data = nafstat.collate.load_all()
        return list(filter_data(data))


def create_json(filename, coach_list=False):
    import json
    data = load_data(coach_list)

    with open(filename, "w") as json_file:
        json.dump(data, json_file, indent=2)


def add_arguments(args, default_source="data/"):
    LOG.debug("add_arguments debug")
    args.add_argument("source", nargs="?",help="Optional path to the source directory. ", default=default_source)
    args.add_argument("target", help="Output filename")
    return args


def run_with_arguments(arguments):
    LOG.info("JSON export started at %s", datetime.datetime.now().isoformat())
    LOG.debug(arguments)
    create_json(arguments.target, arguments.coach_list)


def main():
    import sys
    argument_parser = argparse.ArgumentParser()
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--debug" is sys.argv else logging.INFO, format=log_format)

    argument_parser.add_argument("--source", help="source", default="data/")

    argument_parser = add_arguments(argument_parser)

    arguments = argument_parser.parse_args()

    run_with_arguments(arguments)


if __name__ == "__main__":
    main()
