#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import time
import logging
from nafstat.tournament import tournamentlist
import nafstat.tournament.fetch_tournament
import nafstat.tournament.fetch_tournamentmatch

LOG = logging.getLogger(__package__)


def update_tournament(t, throttle = True):
    LOG.info("Tournament %s", nafstat.tournament.tournamentlist.tournament_line(t))
    LOG.debug("Downloading tournament data")

    tournament_start = time.time()
    nafstat.tournament.fetch_tournament.fetch_tournament(t["tournament_id"])
    tournament_wait = time.time()-tournament_start

    if throttle:
        LOG.debug("Waiting %ss", tournament_wait)
        time.sleep(tournament_wait)

    LOG.debug("Downloading tournament matches")

    matches_start = time.time()
    nafstat.tournament.fetch_tournamentmatch.fetch_tournamentmatch(t["tournament_id"])
    matches_wait = time.time()-matches_start
    if throttle:
        LOG.debug("Waiting %ss", matches_wait)
        time.sleep(matches_wait)


def update_list(tournaments):
    LOG.debug("%s recent tournaments", len(tournaments))
    for idx, t in enumerate(tournaments):
        update_tournament(t)


def update():
    """ Download recent tournaments from thenaf.net  """
    LOG.info("Updating NAF data")

    recent_tournaments = list(tournamentlist.recent(tournamentlist.list_tournaments()))
    LOG.info("{} recent tournament{}".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))
    update_list(recent_tournaments[0:5])

    new_tournaments = list(tournamentlist.no_data(tournamentlist.list_tournaments()))
    LOG.info("{} new tournament{}".format(len(new_tournaments), "s" if len(new_tournaments) != 1 else ""))
    update_list(new_tournaments)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--DEBUG" in sys.argv else logging.INFO, format=log_format)
    update()


if __name__ == "__main__":
    main()