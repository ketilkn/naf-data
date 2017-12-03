#!/usr/bin/env python
"""  Load tournaments from file """
import sys
import logging
import os.path
from bs4 import BeautifulSoup

LOG = logging.getLogger(__package__)



def parse_row(columns):
    if len(columns)!=5:
        LOG.warning(f"Unexpected column count {len(columns)}")

    anchor = columns[0].select_one("a")

    if not anchor or not anchor.has_attr("href"):
        LOG.error("Missing anchor in column 0")
        LOG.error(anchor)
        LOG.error(columns[0])
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
    LOG.debug(f"Parsing {len(rows)} rows")
    if len(rows)<3:
        LOG.warning(f"Expected lots of rows(Usually 3100+), found {len(rows)}")
    result = []
    LOG.debug("Skipping first two rows")

    for row in rows[2:]:
        parsed_row = parse_row(row.select("td"))
        result.append(parsed_row)

    LOG.info(f"Finished parsing {len(result)} rows")
    return result


def parse_table(table):
    LOG.debug("Parsing table")
    rows = table.select("tr")
    return parse_rows(rows)


def parse_file(soup):
    LOG.debug("Loading 'div.pn-box1 table' from soup")
    tables = soup.select("div.pn-box1 table")
    if len(tables)!=2:
        LOG.error(f"Unexpected table count {len(tables)}, 2 expected")
        #return []
    return parse_table(tables[1])


def load(filename="data/naf_tourneys.html"):
    LOG.info(f"Loading tournaments from {filename}")
    if not os.path.exists(filename):
        LOG.error(f"{filename} does not exist")
        sys.exit("Unrecoverable error")
    if not os.path.isfile(filename):
        LOG.error(f"{filename} is not a file")
        sys.exit("Unrecoverable error")

    with open(filename, "rb") as f:
        LOG.debug("Decode UTF-8")
        data = f.read().decode("UTF-8")
        LOG.debug("Parsing file using bs4 lxml")
        return parse_file(BeautifulSoup(data, "lxml"))
    LOG.warning(f"No data loading {filename}")



def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)12s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    LOG.debug("tourney.py main")
    filename = "data/naf_tourneys.html" if len(sys.argv) < 2 else sys.argv[1]
    result = list(load(filename)[:10])
    LOG.info("Showing first 10 results")
    pprint(result, indent=2)





if __name__ == "__main__":
    main()