#!/usr/bin/env python
"""  Parse match from HTML """
import logging
from nafparser import fetch_tournamentlist

LOG = logging.getLogger(__package__)
DEFAULT_TARGET = "data/matches/m{}.html"
TOURNAMENT_MATCH_URL = "https://member.thenaf.net/index.php?module=NAF&type=view&id={}&advanced=1"


def fetch_tournamentmatch(tournament_id, url = TOURNAMENT_MATCH_URL, target = DEFAULT_TARGET):
    LOG.debug("Fetch tournament %s", tournament_id)
    return fetch_tournamentlist.fetch_url(url.format(tournament_id), target.format(tournament_id), True)


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    data_for_tournament = fetch_tournamentmatch("3154")
    print(data_for_tournament)


if __name__ == "__main__":
    main()