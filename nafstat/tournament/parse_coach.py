#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging
import re
from bs4.element import NavigableString

from nafstat.file_loader import load
from nafstat.tournament.parse_tournament import row_with_heading

LOG = logging.getLogger(__package__)


def parse_coach_info(table):
    LOG.debug("parse_coach info for table %s", table)

    return {"naf_number": row_with_heading(table, "NAF number").strip(),
            "naf_name": row_with_heading(table, "NAF name").strip(),
            "nation": row_with_heading(table, "Nation").strip()}


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
            LOG.warning("-1 matches for %s %s", naf_number, race["race"])

    return races


def parse_coach(soup):
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
    LOG.debug(f"Found {len(tables)} tables")

    coach_info = parse_coach_info(tables[0])

    if not coach_info["naf_name"] and not coach_info["nation"]:
        LOG.debug("No naf_name and no nation. Returning None")
        return None

    summary_stats = parse_summary_stats(tables[1])
    blood_bowl_rankings = parse_blood_bowl_rankings(tables[2], coach_info["naf_number"]) if len(tables) > 2 else {}

    coach_info["summary"] = summary_stats
    coach_info["ranking"] = blood_bowl_rankings

    return coach_info


def main():
    import os
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    LOG.debug("parse_matches.py main")
    filename = "data/coach/c{}.html".format("1305" if len(sys.argv) < 2 else sys.argv[1])

    result = load(parse_coach, filename)
    pprint(result, indent=2)


if __name__ == "__main__":
    main()