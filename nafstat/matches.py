#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging

from .__main__ import load

LOG = logging.getLogger(__package__)

def parse_rows(rows):
    LOG.debug("Parsing rows")

    return []


def parse_table(soup):
    LOG.debug("Parsing table ")

    return []


def parse_match(soup):
    LOG.debug("Parsing matches")

    maincontent = soup.select_one("#pn-maincontent")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return []

    maincontent = soup.select_one("#pn-maincontent ")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return []

    table = maincontent.select_one("table")
    if not table:
        LOG.error("match table not found")
        return []

    return parse_table(table)


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    LOG.debug("matches.py main")
    filename = "data/matches/m3154.html" if len(sys.argv) < 2 else sys.argv[1]

    result = list(load(parse_match, filename))
    if len(result) > 0:
        pprint(result, indent=2)
    else:
        LOG.warning(f"No data loading {filename}")
        LOG.warning("Did you supply the correct filename?")
        LOG.info(f"No matches found in file f{filename}")


if __name__ == "__main__":
    main()