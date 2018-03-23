#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import time
import datetime
import logging
import logging.config
import argparse
import humanfriendly
import nafstat.update_tournament
import nafstat.update_coach
from nafstat.tournament import tournamentlist
import nafstat.tournament.fetch_tournament
import nafstat.tournament.fetch_tournamentmatch
import nafstat.collate
import nafstat.coachlist

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


def update_recent(throttle=True, recent=16):
    recent_tournaments = list(tournamentlist.recent(tournamentlist.list_tournaments(), number_of_days=recent))
    LOG.info("Found {} recent tournament{}".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))

    if recent_tournaments:
        nafstat.update_tournament.update_tournaments(recent_tournaments, throttle)
        recent_coaches = nafstat.tournament.tournamentlist.coaches_by_tournaments(recent_tournaments)
        all_coaches = set(nafstat.coachlist.load_dict_by_name().keys())

        nafstat.update_coach.update_coaches_by_nick(recent_coaches.difference(all_coaches), throttle)


def update_new(throttle=True):
    new_tournaments = list(tournamentlist.no_data(tournamentlist.list_tournaments()))
    LOG.info("Found {} new tournament{}".format(len(new_tournaments), "s" if len(new_tournaments) != 1 else ""))

    if new_tournaments:
        nafstat.update_tournament.update_tournaments(new_tournaments, throttle)


def update(throttle=True, recent=16):
    """ Download recent tournaments from thenaf.net  """
    LOG.info("Updating NAF data")
    if not throttle:
        LOG.warning("No delay between requests")
    else:
        LOG.debug("Politely using delay between requests")

    update_new(throttle)
    update_recent(throttle, recent=recent)


def main():
    LOG.info("Update started at %s", datetime.datetime.now().isoformat())
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--no-throttle", help="No delay between requests", action="store_true")
    argument_parser.add_argument("--recent", help="Download tournaments from the last n days", type=int, default=16)
    arguments = argument_parser.parse_args()


    start = time.time()
    update(throttle=not arguments.no_throttle, recent=arguments.recent)
    LOG.info("Update ended after %s at %s",
             humanfriendly.format_timespan(time.time() - start),
             datetime.datetime.now().isoformat())


if __name__ == "__main__":
    main()