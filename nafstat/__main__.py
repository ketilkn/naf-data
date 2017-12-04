#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import os.path
import logging

from bs4 import BeautifulSoup

LOG = logging.getLogger(__package__)

def load(parser=None, filename="data/naf_tourneys.html"):
    LOG.info(f"Loading data from {filename}")
    if not os.path.exists(filename):
        LOG.error(f"{filename} does not exist")
        sys.exit("Unrecoverable error")
    if not os.path.isfile(filename):
        LOG.error(f"{filename} is not a file")
        sys.exit("Unrecoverable error")

    with open(filename, "rb") as f:
        LOG.debug("Decode UTF-8")
        try:
            data = f.read().decode("UTF-8")
            LOG.debug("Parsing file using bs4 lxml")
            result = parser(BeautifulSoup(data, "lxml"))
            if result is None:
                LOG.error(f"Parser {parser.__name__} returned None for {filename}")
                return []
            return result
        except UnicodeDecodeError as ex:
            LOG.exception(ex)
            LOG.error(f"Expected character set UTF-8 for input file {filename}")

    return []


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)


if __name__ == "__main__":
    main()