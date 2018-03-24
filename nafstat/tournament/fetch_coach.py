#!/usr/bin/env python
"""  Parse match from HTML """
import logging
import requests
from nafstat.tournament import fetch_tournamentlist
import nafstat.file_loader
import nafstat.tournament.parse_coach

LOG = logging.getLogger(__package__)

DEFAULT_TARGET = "data/coach/c{}.html"
COACH_URL = "https://member.thenaf.net/index.php?module=NAF&type=coachpage&coach={}"


def fetch_coach(coach_id, url=COACH_URL, target=DEFAULT_TARGET):
    LOG.debug("fetch_coach %s", coach_id)
    result = fetch_tournamentlist.fetch_tournamentlist(url=COACH_URL.format(coach_id), target=target.format(coach_id))
    return result


def fetch_coach_by_nick(coach_id, url=COACH_URL, target=None):
    LOG.debug("fetch_coach_by_nick %s", coach_id)

    url_to_get = url.format(coach_id)
    response = requests.get(url_to_get)
    if not response.history and response.status_code == 200:
        html = response.text
        soup = nafstat.file_loader.load_soup(html)
        coach = nafstat.tournament.parse_coach.parse_coach(soup)
        if "naf_number" in coach:
            LOG.debug("Naf number is %s", coach["naf_number"])
            LOG.debug("Naf name is %s", coach["naf_name"])

            filename = target if target else DEFAULT_TARGET.format(coach["naf_number"])
            LOG.debug("Open file %s for writing", filename)
            with open(filename, "w") as coach_file:
                coach_file.write(html)
                return filename
        else:
            LOG.warning("No naf_number for %s", url_to_get)
    else:
        LOG.warning("Response %s %s for %s", response.status_code, response.reason, url_to_get)

    return False


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    import sys

    coach_to_find = sys.argv[1] if len(sys.argv) > 1 else "12403"

    if coach_to_find.isdigit():
        fetch_coach(coach_to_find, COACH_URL.format(coach_to_find))
    else:
        fetch_coach_by_nick(coach_to_find, COACH_URL.format(coach_to_find))


if __name__ == "__main__":
    main()