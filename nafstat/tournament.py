#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging
from bs4.element import NavigableString

from .__main__ import load

LOG = logging.getLogger(__package__)




def row_with_heading(table, heading):
    LOG.debug(f"Searching for heading {heading}")
    for row in table.children:
        if isinstance(row, NavigableString):
            continue
        LOG.debug(f"raden: {row}")
        columns = list(row.children)
        LOG.debug(f"{len(columns)} children {columns}")
        if columns[0] and heading in columns[0].text:
            LOG.debug(f"Found {heading} with content '{columns[1].text}'")
            if columns[1].select_one("a"):
                return columns[1].select_one("a")["href"] if columns[1].select_one("a").has_attr("href") else columns[1].text
            return columns[1].text
    LOG.debug(f"{heading} not found")
    return None


def parse_tables(tables):
    soup = tables[0]
    style = row_with_heading(soup, "Style")
    scoring = row_with_heading(soup, "Scoring")
    type = row_with_heading(soup, "Type")
    email = row_with_heading(soup, "Email")
    webpage = row_with_heading(soup, "Webpage")
    start_date = row_with_heading(soup, "Start Date")
    end_date = row_with_heading(soup, "End Date")
    organizer = row_with_heading(soup, "Organizer")

    more = tables[1]

    information = more.find_all("tr")[8].text



    return {"style": style,
            "scoring": scoring,
            "organizer": organizer,
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
            "email": email,
            "webpage": webpage,
            "information": information}


def parse_tournament(soup):
    LOG.debug("Parsing tournament")

    maincontent = soup.select_one("#pn-maincontent")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return []

    maincontent = soup.select_one("#pn-maincontent ")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return []

    tables = list(maincontent.select("table table[border=0]"))
    if not tables:
        LOG.error("match table not found")
        return []
    LOG.debug(f"Found {len(tables)} tables")

    return parse_tables(tables)


def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    LOG.debug("matches.py main")
    filename = "data/tournaments/t3154.html" if len(sys.argv) < 2 else sys.argv[1]

    result = load(parse_tournament, filename)
    if len(result) > 0:
        pprint(result, indent=2)
    else:
        LOG.warning(f"No data loading {filename}")
        LOG.warning("Did you supply the correct filename?")
        LOG.info(f"No matches found in file f{filename}")


if __name__ == "__main__":
    main()