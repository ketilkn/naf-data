#!/usr/bin/env python
""" Export data to sqlite """
import datetime
import argparse
import logging.config

import nafstat.dbexport.to_sqlite
import nafstat.all_matches
import nafstat.all_coaches
import nafstat.export_json

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=False)
LOG = logging.getLogger(__name__)


def add_arguments(args, default_source="data/"):
    LOG.debug("add_arguments debug")
    args.add_argument("type", choices=["sqlite", "sqlite3", "csv", "json"], help="Export format")
    args.add_argument("source", nargs="?",help="Optional path to the source directory. ", default=default_source)
    args.add_argument("target", help="Output filename")
    args.add_argument("--coach-list", help="Dump list of coaches (csv/json)", action="store_true")
    args.add_argument("--debug", help="Log level debug", action="store_true")
    return args


def run_with_arguments(arguments):
    LOG.info("Export %s started at %s", arguments.type, datetime.datetime.now().isoformat())
    LOG.debug(arguments)

    if arguments.type in ["sqlite", "sqlite3"]:
        nafstat.dbexport.to_sqlite.to_db(arguments.target)
    elif arguments.type == "csv" and arguments.coach_list:
        nafstat.all_coaches.run_with_arguments(arguments)
    elif arguments.type == "csv":
        nafstat.all_matches.run_with_arguments(arguments)
    elif arguments.type == "json":
        nafstat.export_json.run_with_arguments(arguments)


def main():
    import sys
    argument_parser = argparse.ArgumentParser()
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--debug" == sys.argv else logging.INFO, format=log_format)

    argument_parser.add_argument("--source", help="source", default="data/")

    argument_parser = add_arguments(argument_parser)

    arguments = argument_parser.parse_args()

    run_with_arguments(arguments)


if __name__ == "__main__":
    main()
