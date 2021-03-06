#!/usr/bin/env python
"""  Parse match from HTML """
import logging

from tqdm import tqdm
import nafstat.update
from nafstat import tournamentlist, fetch_tournament, fetch_tournamentmatch

LOG = logging.getLogger(__package__)


def update_tournament(tournament, throttle=True):
    LOG.debug("Tournament %s", tournamentlist.tournament_line(tournament))

    LOG.debug("Downloading tournament data")
    nafstat.update.download(fetch_tournament.fetch_tournament, tournament)

    LOG.debug("Downloading tournament matches")
    nafstat.update.download(fetch_tournamentmatch.fetch_tournamentmatch, tournament)


def update_tournaments(tournaments, throttle=True):
    LOG.debug("Updating %s tournaments", len(tournaments))
    for idx, t in enumerate(tqdm(tournaments)):
        update_tournament(t, throttle)


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    selected_tournaments = list(tournamentlist.recent(tournamentlist.list_tournaments(), 180))
    LOG.info("Found {} tournament{} in selection".format(len(selected_tournaments), "s" if len(selected_tournaments) != 1 else ""))

    import random
    random_tournament1 = random.choice(selected_tournaments)

    LOG.info("%s '%s' selected at random", random_tournament1["tournament_id"], random_tournament1["name"])

    if random_tournament1:
        nafstat.update_tournament.update_tournaments([random_tournament1], throttle=True)


if __name__ == "__main__":
    main()
