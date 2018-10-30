#!/usr/bin/env python
""" Export data to sqlite """
import datetime
import argparse
import logging.config

import nafstat.dbexport.to_sqlite

logging.config.fileConfig('pylogging.conf')
LOG = logging.getLogger("nafstat.to_db")


def main():
    import sys
    argument_parser = argparse.ArgumentParser()
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--debug" is sys.argv else logging.INFO, format=log_format)

    LOG.info("Export started at %s", datetime.datetime.now().isoformat())
    argument_parser.add_argument("filename", help="filename")
    argument_parser.add_argument("--debug", help="Log level debug", action="store_true")
    argument_parser.add_argument("--recent",
                                 help="Download tournaments from the last n days. default 16",
                                 type=int, default=16)
    arguments = argument_parser.parse_args()

    nafstat.dbexport.to_sqlite.to_db(arguments.filename)


if __name__ == "__main__":
    main()
