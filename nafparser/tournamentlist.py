#!/usr/bin/env python
"""  Load tournaments from file """
import sys
import logging
import typing
import os.path
import bs4
from bs4 import BeautifulSoup
from nafstat.file_loader import load

LOG = logging.getLogger(__package__)
PARSE_LOG = logging.getLogger("parselog")


def parse_row(columns):
    if len(columns)!=5:
        PARSE_LOG.warning("Unexpected column count %s", len(columns))

    anchor = columns[0].select_one("a")

    if not anchor or not anchor.has_attr("href"):
        PARSE_LOG.error("Missing anchor in column 0")
        PARSE_LOG.error(anchor)
        PARSE_LOG.error(columns[0])
        sys.exit("Unrecoverable error")

    tournament_id = anchor["href"][anchor["href"].rindex("=")+1:]
    name=columns[0].text
    location=columns[1].text
    start_date=columns[2].text
    end_date = columns[3].text
    variant = columns[4].text
    return {"name": name,
                "tournament_id": tournament_id,
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "variant": variant}


def parse_rows(rows):
    PARSE_LOG.debug("Parsing %s {} rows", len(rows))
    if len(rows)<3:
        PARSE_LOG.warning("Expected lots of rows(Usually 3100+), found {}", len(rows))
    result = []
    PARSE_LOG.debug("Skipping first two rows")

    for row in rows[2:]:
        parsed_row = parse_row(row.select("td"))
        result.append(parsed_row)

    PARSE_LOG.info("Finished parsing %s rows", len(result))
    return result


def parse_table(table):
    PARSE_LOG.debug("Parsing table")
    rows = table.select("tr")
    return parse_rows(rows)


def parse_html(html: str) -> typing.List[typing.Dict]:
    """Parse html into list of tournaments

    Parameters:
    html(str): HTML source of tourney page

    Returns:
    List of tournament dicts with
        tournament_id
        location
        start_date
        end_date
        variant
    """
    soup = bs4.BeautifulSoup(html, 'lxml')
    return parse_soup(soup)


def parse_soup(soup: str):
    LOG.debug("Parsing tournament list")
    PARSE_LOG.debug("Loading 'div.pn-box1 table' from soup")
    tables = soup.select("div.pn-box1 table")
    if len(tables)!=2:
        PARSE_LOG.error("Unexpected table count %s, 2 expected", len(tables))
        #return []
    tournaments = parse_table(tables[1])
    LOG.debug("Found %s tournaments", len(tournaments))
    return tournaments


def load2(parser, filename="data/naf_tourneys.html"):
    PARSE_LOG.info("Loading tournaments from %s", filename)
    if not os.path.exists(filename):
        PARSE_LOG.error("%s does not exist", filename)
        sys.exit("Unrecoverable error")
    if not os.path.isfile(filename):
        PARSE_LOG.error("%s is not a file", filename)
        sys.exit("Unrecoverable error")

    with open(filename, "rb") as f:
        PARSE_LOG.debug("Decode UTF-8")
        try:
            data = f.read().decode("UTF-8")
            PARSE_LOG.debug("Parsing file using bs4 lxml")
            return parser(BeautifulSoup(data, "lxml"))
        except UnicodeDecodeError as ex:
            PARSE_LOG.exception(ex)
            PARSE_LOG.error("Expected character set UTF-8 for input file %s", filename)

    return []


def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)12s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    PARSE_LOG.debug("parse_tournamentlist.py main")
    filename = "data/naf_tourneys.html" if len(sys.argv) < 2 else sys.argv[1]

    result = list(load(parse_html, filename))
    if len(result) > 0:
        PARSE_LOG.info("Showing first 10 results")
        pprint(result[:10], indent=2)
    else:
        PARSE_LOG.warning("No data loading %s", filename)
        PARSE_LOG.warning("Did you supply the correct filename?")
        PARSE_LOG.info("No tournaments found in file %s", filename)


if __name__ == "__main__":
    main()
