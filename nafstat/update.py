#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import time
import datetime
import logging.config
import argparse
import humanfriendly
from nafstat.session import throttle_by_request_time
import nafstat.update_tournament
import nafstat.update_coach
from nafstat.tournament import tournamentlist
import nafstat.tournament.fetch_tournament
import nafstat.tournament.fetch_tournamentmatch
import nafstat.collate
import nafstat.coachlist

logging.config.fileConfig('pylogging.conf')
LOG = logging.getLogger("nafstat.update")


@throttle_by_request_time
def download(downloader, tournament):
    LOG.debug("Using downloader %s with id %s", downloader.__name__, tournament["tournament_id"])
    downloader(tournament["tournament_id"])


def update_recent(recent=16, force_coach=False):
    """Download recent tournaments and the participants from thenaf.net
    recent(int) - number of days to consider recent
    force_coach(boolean) - redownload existing coaches in data/coach
    """
    recent_tournaments = list(tournamentlist.recent(tournamentlist.list_tournaments(), number_of_days=recent))
    LOG.info("Found {} recent tournament{}".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))

    if recent_tournaments:
        nafstat.update_tournament.update_tournaments(recent_tournaments)
        recent_coaches = nafstat.tournament.tournamentlist.coaches_by_tournaments(recent_tournaments)
        all_coaches = set(nafstat.coachlist.load_dict_by_name().keys())

        coaches_to_download = recent_coaches.difference(all_coaches) if not force_coach else recent_coaches

        nafstat.update_coach.update_coaches_by_nick(coaches_to_download)


def update_new():
    """Download new future tournaments from thenaf.net"""
    new_tournaments = list(tournamentlist.no_data(tournamentlist.list_tournaments()))
    LOG.info("Found {} new tournament{}".format(len(new_tournaments), "s" if len(new_tournaments) != 1 else ""))

    if new_tournaments:
        nafstat.update_tournament.update_tournaments(new_tournaments)


def update(throttle=True, recent=16, new=True, force_coach=False):
    """Update tournaments from thenaf.net"""
    print("name: {}".format(__name__))
    print("package:".format(__package__))
    LOG.info("Updating NAF data")
    if not throttle:
        LOG.warning("No delay between requests")
    else:
        LOG.debug("Politely using delay between requests")

    if new:
        update_new()
    if recent:
        update_recent(recent=recent, force_coach=force_coach)


def main():
    LOG.info("Update started at %s", datetime.datetime.now().isoformat())
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("--throttle", help="Delay between requests (default)", action="store_true")
    argument_parser.add_argument("--no-throttle", help="No delay between requests", action="store_true")
    argument_parser.add_argument("--force-coach", help="Download all coaches", action="store_true")
    argument_parser.add_argument("--skip-new", help="Skip new tournaments", action="store_true", default=False)
    argument_parser.add_argument("--recent",
                                 help="Download tournaments from the last n days. default 16",
                                 type=int, default=16)
    arguments = argument_parser.parse_args()

    print("name: {}".format(__name__))
    print("package:".format(__package__))
    start = time.time()
    update(recent=arguments.recent,
           new=not arguments.skip_new,
           force_coach=arguments.force_coach)

    LOG.info("Update ended after %s at %s",
             humanfriendly.format_timespan(time.time() - start),
             datetime.datetime.now().isoformat())


if __name__ == "__main__":
    main()
