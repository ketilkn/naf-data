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


def update_tournaments_with_missing_coaches():
    LOG.debug("Try update tournaments with unknown coaches")
    tournaments_with_unknowns = tournamentlist.unknown_coaches(tournamentlist.load_tournaments())

    LOG.info("Found {} tournament{} with unknown coaches".format(len(tournaments_with_unknowns), "s" if len(tournaments_with_unknowns) != 1 else ""))
    update_tournaments(tournaments_with_unknowns, force_coach=False)


def update_invalid_coaches():
    LOG.debug("Try to update coaches with invalid data")
    invalid_coaches = [coach["naf_name"] for coach in nafstat.coachlist.load_invalid()]
    nafstat.update_coach.update_coaches_by_nick(invalid_coaches)


def update_tournaments(recent_tournaments, force_coach):
    LOG.info("Update tournaments")
    nafstat.update_tournament.update_tournaments(recent_tournaments)
    recent_coaches = nafstat.tournament.tournamentlist.coaches_by_tournaments(recent_tournaments)

    LOG.debug("Loading all coaches")
    all_coaches = set(nafstat.coachlist.load_dict_by_name().keys())

    coaches_to_download = recent_coaches.difference(all_coaches) if not force_coach else recent_coaches

    LOG.info("Update coaches")
    LOG.debug("Need to update %s coaches", len(coaches_to_download))
    nafstat.update_coach.update_coaches_by_nick(coaches_to_download)


def update_recent(recent=16, force_coach=False):
    """Download recent tournaments and the participants from thenaf.net
    recent(int) - number of days to consider recent
    force_coach(boolean) - redownload existing coaches in data/coach
    """
    recent_tournaments = list(tournamentlist.recent(tournamentlist.load_tournaments(), number_of_days=recent))
    LOG.info("Found {} recent tournament{}".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))
    if not force_coach:
        recent_tournaments =  tournamentlist.no_matches(recent_tournaments)
        LOG.info("Found {} recent tournament{} with no matches".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))

    if recent_tournaments:
        update_tournaments(recent_tournaments, force_coach)


def update_new():
    """Download new future tournaments from thenaf.net"""
    new_tournaments = list(tournamentlist.no_data(tournamentlist.load_tournaments()))
    LOG.info("Found {} new tournament{}".format(len(new_tournaments), "s" if len(new_tournaments) != 1 else ""))
    if new_tournaments:
        nafstat.update_tournament.update_tournaments(new_tournaments)


def update_by_id(tournament_ids, force_coach=False):
    """Download tournaments with ids in tournaments_ids """
    tournaments = list(tournamentlist.by_id(ids=tournament_ids, tournaments=tournamentlist.load_tournaments()))
    update_tournaments(tournaments, force_coach)


def update(throttle=True, recent=16, new=True, force_coach=False):
    """Update tournaments from thenaf.net"""
    LOG.debug("Updating NAF data")
    if not throttle:
        LOG.warning("No delay between requests")
    else:
        LOG.debug("Politely using delay between requests")

    if new:
        update_new()
    if recent:
        update_recent(recent=recent, force_coach=force_coach)
    update_invalid_coaches()
    update_tournaments_with_missing_coaches()


def add_arguments(arg, default_source="data/"):
    arg.add_argument("source", nargs="?", default=default_source, 
            help="Optional path to the source directory default: {}".format(default_source))
    #arg.add_argument("target", help="Path to the destination directory")
    arg.add_argument("--debug", help="Log level debug", action="store_true")
    arg.add_argument("--source", help="source", default="data/")
    arg.add_argument("--recent",
                                 help="Download tournaments from the last n days. default 16",
                                 type=int, default=16)
    arg.add_argument("--throttle", action="store_true", 
            help="Delay between requests (default)")
    arg.add_argument("--no-throttle", action="store_true",
            help="No delay between requests")
    arg.add_argument("--force-coach", action="store_true",
            help="Download all coaches")
    arg.add_argument("--skip-new", action="store_true", default=False, 
            help="Skip new tournaments")
    arg.add_argument("--fix-missing", action="store_true",
                     help="Redownload tournaments with unknown coaches")
    arg.add_argument("--tournament", type=str, nargs="+",
            help="Update tournaments by id")
    return arg


def run_with_arguments(arguments):
    LOG.info("Update started at %s", datetime.datetime.now().isoformat())
    LOG.debug(arguments)
    start = time.time()
    if arguments.fix_missing:
        update_tournaments_with_missing_coaches()
    elif arguments.tournament:
        update_by_id(arguments.tournament, force_coach=arguments.force_coach)
    else:
        update(recent=arguments.recent,
               new=not arguments.skip_new,
               force_coach=arguments.force_coach)

    LOG.info("Update ended after %s at %s", humanfriendly.format_timespan(time.time() - start),
                 datetime.datetime.now().isoformat())


def main():
    argument_parser = argparse.ArgumentParser()
    add_arguments(argument_parser)
    arguments = argument_parser.parse_args()

    run_with_arguments(arguments)


if __name__ == "__main__":
    main()
