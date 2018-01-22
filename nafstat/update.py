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


def update_list(tournaments):
    LOG.debug("%s recent tournaments", len(tournaments))
    for idx, t in enumerate(tournaments):
        if idx > 0:
            LOG.debug("Waiting 2 seconds")
            time.sleep(2)
        update_tournament(t)



def update():
    """ Download recent tournaments from thenaf.net  """
    LOG.info("Updating NAF data")
    recent_tournaments = list(
        nafstat.tournament.tournamentlist.recent(
            nafstat.tournament.tournamentlist.list_tournaments()
        ))

    update_list(recent_tournaments)

    new_tournaments = list(nafstat.tournament.tournamentlist.no_data(nafstat.tournament.tournamentlist.list_tournaments()))

    update_list(new_tournaments)



def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--DEBUG" in sys.argv else logging.INFO, format=log_format)
    update()


if __name__ == "__main__":
    main()