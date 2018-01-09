#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import time
import logging
import nafstat.tournament.tournamentlist
import nafstat.tournament.fetch_tournament
import nafstat.tournament.fetch_tournamentmatch

LOG = logging.getLogger(__package__)


def update_tournament(t):
    LOG.info("Tournament %s", nafstat.tournament.tournamentlist.tournament_line(t))
    LOG.debug("Downloading tournament data")
    nafstat.tournament.fetch_tournament.fetch_tournament(t["tournament_id"])
    time.sleep(1)
    LOG.debug("Downloading tournament matches")
    nafstat.tournament.fetch_tournamentmatch.fetch_tournamentmatch(t["tournament_id"])


def update():
    """ Download recent tournaments from thenaf.net  """
    LOG.info("Updating NAF data")
    recent_tournaments = list(
        nafstat.tournament.tournamentlist.recent(
            nafstat.tournament.tournamentlist.list_tournaments()
        ))

    LOG.debug("%s recent tournaments", len(recent_tournaments))
    for idx, t in enumerate(recent_tournaments):
        if idx > 0:
            LOG.debug("Waiting 2 seconds")
            time.sleep(2)
        update_tournament(t)


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    update()


if __name__ == "__main__":
    main()