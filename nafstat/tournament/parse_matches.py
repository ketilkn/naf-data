#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging

from nafstat.__main__ import load

LOG = logging.getLogger(__package__)

def parse_time(row):
    LOG.debug("Parse time")
    column = row.select_one("td")
    if column and len(column.text.strip().split(":")) == 2:
        return column.text.strip()
    return False


def parse_date(row):
    LOG.debug("Parse date")
    column = row.select_one("th")
    if column and len(column.text.strip().split("-")) == 3:
        return column.text.strip()
    else:
        LOG.debug(f"Not a date {row}")
        return False

def parse_match(row):
    LOG.debug("parse_match")
    return False


def parse_row(row, current_date, current_time):
    LOG.debug("parse_row")
    if current_date == "1970-01-01":
        LOG.warning(row)
        LOG.warning(f"Current date is default")
    if current_time == "99:99":
        LOG.warning(row)
        LOG.warning(f"Current time is default")

    columns = list(row.children)
    if len(columns) != 14:
        LOG.warning(f"Row count {len(columns)} expected 14")
        LOG.debug(row)
        sys.exit("Unrecoverable error")

    home_result = "T"
    away_result = "T"

    home_score = columns[6].select("td")[0].text
    away_score = columns[6].select("td")[2].text

    if home_score > away_score:
        home_result = "W"
        away_result = "L"
    if home_score < away_score:
        home_result = "L"
        away_result = "W"

    home_casualties = [int(val) for val in columns[4].text.split("|")]
    away_casualties = [int(val) for val in columns[10].text.split("|")]

    return {"date": current_date,
            "time": current_time,
            "match_id": columns[0].text,
            "home_coach": columns[1].text,
            "home_race": columns[2].text,
            "home_score": home_score,
            "home_result": home_result,
            "home_tr": columns[3].text,
            "home_cas": sum(home_casualties),
            "home_bh": home_casualties[0],
            "home_si": home_casualties[1],
            "home_dead": home_casualties[2],
            "home_winnings": columns[5].text,
            "away_coach": columns[7].text,
            "away_race": columns[8].text,
            "away_score": away_score,
            "away_result": away_result,
            "away_tr": columns[9].text,
            "away_cas": sum(away_casualties),
            "away_bh": away_casualties[0],
            "away_si": away_casualties[1],
            "away_dead": away_casualties[2],
            "gate": columns[12].text,
            "variant": columns[13].text}



def parse_rows(rows):
    LOG.debug("Parsing rows")

    match_date = "1970-01-01"
    match_time = "99:99"

    result = []

    for row in rows:
        if parse_date(row):
            match_date = parse_date(row)
        elif parse_time(row):
            match_time = parse_time(row)
        elif parse_row(row, match_date, match_time):
            result.append(parse_row(row, match_date, match_time))

    return result


def parse_table(soup):
    LOG.debug("Parsing table ")

    rows = list(soup.children)
    LOG.debug(f"{len(rows)} rows in table")
    return parse_rows(rows[2:])


def parse_match(soup):
    LOG.debug("Parsing matches")

    maincontent = soup.select_one("#pn-maincontent")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return None

    maincontent = soup.select_one("#pn-maincontent ")
    if not maincontent:
        LOG.error("#pn-maincontent not found")
        return None

    table = maincontent.select_one("table")
    if not table:
        LOG.debug("match table not found")
        if "There are no games to view for this tournament." in maincontent.text:
            LOG.debug("Found: There are no games to view for this tournament")
            return []
        else:
            LOG.debug(maincontent)
            LOG.error("No matches found. Unexpected content in #pn-maincontent.")
            return None

    return parse_table(table)


def main():
    from pprint import pprint
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