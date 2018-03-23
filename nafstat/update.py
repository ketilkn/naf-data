#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import time
import logging
from nafstat.tournament import tournamentlist
import nafstat.tournament.fetch_tournament
import nafstat.tournament.fetch_tournamentmatch

LOG = logging.getLogger(__package__)


def download(downloader, t, throttle=True):
    start_time = time.time()
    LOG.debug("Using downloader %s with id %s", downloader.__name__, t)
    downloader(t["tournament_id"])
    request_time = time.time()-start_time

    if throttle:
        LOG.debug("Waiting %ss", request_time)
        time.sleep(request_time)
    else:
        LOG.debug("Throttle is False")


def update_tournament(t, throttle=True):
    LOG.info("Tournament %s", nafstat.tournament.tournamentlist.tournament_line(t))

    LOG.debug("Downloading tournament data")
    download(nafstat.tournament.fetch_tournament.fetch_tournament, t, throttle)

    LOG.debug("Downloading tournament matches")
    download(nafstat.tournament.fetch_tournamentmatch.fetch_tournamentmatch, t, throttle)


def update_list(tournaments, throttle=True):
    LOG.debug("%s recent tournaments", len(tournaments))
    for idx, t in enumerate(tournaments):
        update_tournament(t, throttle)


def update(throttle=True):
    """ Download recent tournaments from thenaf.net  """
    LOG.info("Updating NAF data")
    if not throttle:
        LOG.warning("No delay between requests")
    else:
        LOG.debug("Politely using delay between requests")

    recent_tournaments = list(tournamentlist.recent(tournamentlist.list_tournaments()))
    LOG.info("{} recent tournament{}".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))
    update_list(recent_tournaments, throttle)

    new_tournaments = list(tournamentlist.no_data(tournamentlist.list_tournaments()))
    LOG.info("{} new tournament{}".format(len(new_tournaments), "s" if len(new_tournaments) != 1 else ""))
    update_list(new_tournaments, throttle)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--DEBUG" in sys.argv else logging.INFO, format=log_format)
    update(throttle="--no-throttle" not in sys.argv)


if __name__ == "__main__":
    main()