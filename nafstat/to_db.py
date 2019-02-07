#!/usr/bin/env python
""" Export data to sqlite """
import datetime
import argparse
import logging.config

import nafstat.dbexport.to_sqlite

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=False)
LOG = logging.getLogger(__name__)

def add_arguments(args, default_source="data/"):
    LOG.debug("add_arguments debug")
    args.add_argument("type", choices=["sqlite", "sqlite3", "csv"], help="Export format")
    args.add_argument("source", nargs="?",help="Optional path to the source directory. ", default=default_source)
    args.add_argument("target", help="Output filename")
    args.add_argument("--debug", help="Log level debug", action="store_true")
    return args


def run_with_arguments(arguments):
    LOG.info("Export started at %s", datetime.datetime.now().isoformat())
    LOG.debug(arguments)
    nafstat.dbexport.to_sqlite.to_db(arguments.target)

def main():
    import sys
    argument_parser = argparse.ArgumentParser()
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--debug" is sys.argv else logging.INFO, format=log_format)

    argument_parser.add_argument("--debug", help="Log level debug", action="store_true")
    argument_parser.add_argument("--source", help="source", default="data/")

    #argument_parser.add_argument("command", choices=["update", "export", "query"], help="export/update")

    argument_parser = add_arguments(argument_parser) 

    arguments = argument_parser.parse_args()

    print(arguments)


if __name__ == "__main__":
    main()
