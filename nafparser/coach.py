#!/usr/bin/env python
"""  Parse match from HTML """
import os.path
import logging
import argparse
import bs4
from nafstat.file_loader import load
from nafparser.tournament import row_with_heading, parse_page_date

PARSE_LOG = logging.getLogger("parselog")
LOG = logging.getLogger(__package__)


def parse_coach_info(table):
    PARSE_LOG.debug("parse_coach info for table %s", table)

    nation = row_with_heading(table, "Nation").strip().capitalize()
    if nation == "Deutschland":
        nation = "Germany"

    return {"naf_number": row_with_heading(table, "NAF number").strip(),
            "naf_name": row_with_heading(table, "NAF name").strip(),
            "nation": nation}


def parse_summary_stats(table):

    tournament_count = row_with_heading(table, "NAF tournaments attended", force_text=True)
    match_count = row_with_heading(table, "NAF ranked games", force_text=True)

    return {"races_played": row_with_heading(table, "Races played"),
            "tournament_count": tournament_count if tournament_count else 0,
            "match_count": match_count if match_count else 0}


def parse_race_rank(row):
    columns = row.select("td")
    matches = int(columns[2].text) if columns[2].text else -1
    return {"race": columns[0].text,
            "elo": float(columns[1].text),
            "matches": matches}


def parse_blood_bowl_rankings(table, naf_number = -1):
    races = {}
    rows = table.select("tr")

    if len(rows) < 3:
        return {}

    for row in rows[2:] if len(rows) > 2 else []:
        race = parse_race_rank(row)
        races[race["race"]]=race
        if race["matches"] == -1:
            PARSE_LOG.warning("-1 matches for %s %s", naf_number, race["race"])

    return races


def parse_soup(soup):
    LOG.debug("Parsing coach")

    maincontent = soup.select_one("#pn-maincontent")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return []

    maincontent = soup.select_one("#pn-maincontent ")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return []

    tables = list(maincontent.select("table[bgcolor=#858390]"))
    if not tables:
        LOG.error("match table not found")
        return []
    PARSE_LOG.debug("Found {} tables".format(len(tables)))

    coach_info = parse_coach_info(tables[0])

    if not coach_info["naf_name"] and not coach_info["nation"]:
        LOG.debug("No naf_name and no nation. Returning None")
        return None

    summary_stats = parse_summary_stats(tables[1])
    blood_bowl_rankings = parse_blood_bowl_rankings(tables[2], coach_info["naf_number"]) if len(tables) > 2 else {}

    coach_info["summary"] = summary_stats
    coach_info["ranking"] = blood_bowl_rankings

    coach_info["_last_updated"] = parse_page_date(soup)

    LOG.debug("Finished parsing coach %s", coach_info["naf_name"])
    return coach_info


def parse_html(html):
    LOG.debug("Parsing coach from HTML")
    soup = bs4.BeautifulSoup(html, "lxml")
    return parse_soup(soup)


def fromfile(filename):
    LOG.debug("Parsing coach from file %s", filename)
    return load(parse_soup, filename)


def do_parse(coach):
    if coach.isnumeric():
        filename = "data/coach/c{}.html".format(coach)
        result = fromfile(filename)
    elif os.path.isfile("data/coach/{}".format(coach)):
        result = fromfile("data/coach/{}".format(coach))
    elif os.path.isfile(coach):
        result = fromfile(coach)
    return result


def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    PARSE_LOG.debug("parse_matches.py main")

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("coach", type=str, nargs="*", default=["1305"],
                                 help="Path, filename or coach id to parse")

    arguments = argument_parser.parse_args()

    for c in arguments.coach:
        coach = do_parse(c)
        pprint(coach, indent=2)


if __name__ == "__main__":
    main()
