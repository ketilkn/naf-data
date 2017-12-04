#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import copy
import logging

from . import tourney
from . import tournament
from . import matches
from .__main__ import load

LOG = logging.getLogger(__package__)


def collate_tournament(tourney, tournament_data, matches):
    tourney.update(tournament_data)
    tourney["matches"]=matches
    return tourney


def load_all():
    LOG.debug("loading all tournaments")
    result = []

    for t in load(tourney.parse_file, "data/naf_tourneys.html"):
        LOG.info(f"Loading {t['tournament_id']} {t['name']}")
        LOG.debug(f"Loading data for {t['tournament_id']}")
        tourney_data = load(tournament.parse_tournament, f"data/tournaments/t{t['tournament_id']}.html")
        LOG.debug(f"Loading matches for {t['tournament_id']}")
        match_data = load(matches.parse_match, f"data/matches/m{t['tournament_id']}.html")
        result.append(collate_tournament(t, tourney_data, match_data))

    return result





def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)

    result = load_all()

    pprint(result[:10], indent=2)




if __name__ == "__main__":
    main()