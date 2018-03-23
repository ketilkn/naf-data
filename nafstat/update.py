#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import time
import datetime
import logging
import logging.config
import humanfriendly
from nafstat.tournament import tournamentlist
import nafstat.tournament.fetch_tournament
import nafstat.tournament.fetch_tournamentmatch

logging.config.fileConfig('pylogging.conf')
LOG = logging.getLogger("nafstat.update")


def download(downloader, tournament, throttle=True):
    start_time = time.time()
    LOG.debug("Using downloader %s with id %s", downloader.__name__, tournament["tournament_id"])
    downloader(tournament["tournament_id"])
    request_time = time.time()-start_time

    if throttle:
        LOG.debug("Waiting %s", humanfriendly.format_timespan(request_time))
        time.sleep(request_time)
    else:
        LOG.debug("Throttle is False")


def update_tournament(tournament, throttle=True):
    LOG.info("Tournament %s", nafstat.tournament.tournamentlist.tournament_line(tournament))

    LOG.debug("Downloading tournament data")
    download(nafstat.tournament.fetch_tournament.fetch_tournament, tournament, throttle)

    LOG.debug("Downloading tournament matches")
    download(nafstat.tournament.fetch_tournamentmatch.fetch_tournamentmatch, tournament, throttle)


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
    LOG.info("Update stared at %s", datetime.datetime.now().isoformat())
    start = time.time()
    update(throttle="--no-throttle" not in sys.argv)
    LOG.info("Update ended after %s at %s", humanfriendly.format_timespan(time.time() - start), datetime.datetime.now().isoformat())


if __name__ == "__main__":
    main()