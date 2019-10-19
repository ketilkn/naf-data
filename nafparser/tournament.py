#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging
import re
from datetime import datetime
from bs4.element import NavigableString

from nafstat.file_loader import load

LOG = logging.getLogger(__package__)
PARSE_LOG = logging.getLogger("parselog")


def row_with_heading(table, heading, force_text=False):
    PARSE_LOG.debug("Searching for heading %s", heading)
    for row in table.children:
        if isinstance(row, NavigableString):
            continue
        PARSE_LOG.debug("raden: %s", row)
        columns = list(row.children)
        PARSE_LOG.debug("%s children %s", len(columns), columns)
        if columns[0] and heading in columns[0].text:
            PARSE_LOG.debug("Found %s with content '%s'", heading, columns[1].text)
            if columns[1].select_one("a") and not force_text:
                return columns[1].select_one("a")["href"] if columns[1].select_one("a").has_attr("href") else columns[1].text
            return columns[1].text
    PARSE_LOG.debug("%s not found", heading)
    return None


def get_other_awards(soup):
    LOG.debug("Looking for award other awards")
    awards = soup.find_all("tr", string="Tournament Statistics")
    other_awards = awards[0].find_next("tr", string='Other Awards')
    result = {}
    if other_awards:
        for award in other_awards.next_siblings:
            if award:
                try:
                    awardee = award.select_one('table td').text.split('(')[0].strip()
                    title = award.find_next('div', {'style': 'color: grey;'}).text.lower()
                    result[title] = awardee
                except AttributeError as ex:
                    LOG.debug('AttributeError')
    return result


def award_row(soup, award_name="Winner"):
    LOG.debug("Looking for award %s", award_name)
    stats = soup.find_all("tr", string="Tournament Statistics")
    if stats:
        award = stats[0].find_next("tr", string=award_name)
        if award:
            if not award.find_next("tr").findChild("h4"):
                awardee = award.find_next("tr").text.split('(')
                return awardee[0].strip() if awardee and awardee[0] else ""
    LOG.debug("Did not find %s", award_name)
    return None


def parse_awards(soup):
    winner = award_row(soup, award_name="Winner")
    runner_up = award_row(soup, award_name="Runner up")
    most_touchdowns = award_row(soup, award_name="Most Touchdowns")
    most_casualties = award_row(soup, award_name="Most Casualties")
    stunty_cup = award_row(soup, award_name="Stunty Cup")
    best_painted = award_row(soup, award_name="Best Painted")
    awards = {"winner": winner,
            "runner up": runner_up,
            "most touchdowns": most_touchdowns,
            "most casualties": most_casualties,
            "stunty cup": stunty_cup,
            "best painted": best_painted, }

    return awards


def parse_page_date(soup):
    found = soup.find_all("td", {"width": "190"})
    if found:
        try:
            found_date = datetime.strptime(found[0].text, '%b %d, %Y - %I:%M %p')
            LOG.debug("Found date %s", found_date)
            return datetime.isoformat(found_date)
        except ValueError:
            LOG.debug("Incorrect dateformat for %s", found[0])
    return "N/A"


def parse_tables(tables):
    soup = tables[0]
    name = row_with_heading(soup, "Tournament Name")
    style = row_with_heading(soup, "Style")
    scoring = row_with_heading(soup, "Scoring")
    tournament_type = row_with_heading(soup, "Type")
    email = row_with_heading(soup, "Email")
    webpage = row_with_heading(soup, "Webpage")
    start_date = row_with_heading(soup, "Start Date")
    end_date = row_with_heading(soup, "End Date")
    organizer = row_with_heading(soup, "Organizer")
    nation = row_with_heading(soup, "Nation")

    more = None

    for table in tables:
        city = row_with_heading(table, "City")
        nation = row_with_heading(table, "Nation")
        for el in table(text=re.compile(r'Tournament Location')):
            PARSE_LOG.debug(el)
            if more:
                PARSE_LOG.warning("Multiple Tournament Location found for '%s'", name)
            more = el.find_parent("table")

    if not more:
        PARSE_LOG.warning("More table not found! Using default")
        more = tables[1]

    more_elements = more.find_all("tr")
    if len(more_elements) < 8:
        PARSE_LOG.warning("more_elements less than 8 for tournament '%s'", name)
        PARSE_LOG.debug(more_elements)
    information = more.find_all("tr")[8].text if len(more_elements) > 8 else "NOT FOUND"

    return {"name": name,
            "style": style,
            "scoring": scoring,
            "type": tournament_type,
            "organizer": organizer,
            "start_date": start_date,
            "end_date": end_date,
            "email": email,
            "webpage": webpage,
            "information": information,
            "nation": nation,
            "city": city}


def parse_soup(soup):
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
    PARSE_LOG.debug("Found %s tables", len(tables))

    tournament = parse_tables(tables)
    tournament["_last_updated"] = parse_page_date(soup)
    tournament["awards"] = parse_awards(soup)
    tournament['other_awards'] = get_other_awards(soup)

    LOG.debug("Finished parsing tournament %s", tournament["name"])
    return tournament


def main():
    from pprint import pprint
    import argparse
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    PARSE_LOG.debug("parse_matches.py main")

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("filenames", type=str, nargs="*", default=["data/tournaments/t3154.html"],
                                 help="Tournament(s) to parse")
    argument_parser.add_argument("--show-key", type=str, nargs="+", help="Show specified key")

    arguments = argument_parser.parse_args()

    for filename in arguments.filenames:
        result = load(parse_soup, filename)
        if len(result) > 0:
            if arguments.show_key:
                for show in arguments.show_key:
                    if show not in result:
                        print("Key {} not found".format(show))
                    else:
                        print("{}: '{}'".format(show, result[show]))
            else:
                pprint(result, indent=2)
        else:
            PARSE_LOG.warning("No data loading %s", filename)
            PARSE_LOG.warning("Did you supply the correct filename?")
            PARSE_LOG.info("No matches found in file %s", filename)


if __name__ == "__main__":
    main()
