#!/usr/bin/env python
"""  Parse match from HTML """
import logging
from nafparser import fetch_tournamentlist

LOG = logging.getLogger(__package__)
DEFAULT_TARGET = "data/tournaments/t{}.html"
TOURNAMENT_MATCH_URL = "https://member.thenaf.net/index.php?module=NAF&type=view&id={}&advanced=1"
TOURNAMENT_URL = "https://member.thenaf.net/index.php?module=NAF&type=tournaments&func=view&id={}"


def fetch_tournament(tournament_id, url = TOURNAMENT_URL, target = DEFAULT_TARGET):
    download_to = target.format(tournament_id)
    LOG.debug("Fetch tournament %s to %s", tournament_id, download_to)
    return fetch_tournamentlist.fetch_url(url.format(tournament_id), download_to, True)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    data_for_tournament = fetch_tournament("3154" if not len(sys.argv) > 1 else sys.argv[1])
    print(data_for_tournament)


if __name__ == "__main__":
    main()