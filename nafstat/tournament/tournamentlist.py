#!/usr/bin/env python
"""  Parse match from HTML """
import datetime
import time
import os
import os.path
import logging
from nafstat.tournament import fetch_tournamentlist
from nafstat.tournament import parse_tournamentlist
from nafstat.tournament import parse_matches
from nafstat.file_loader import load_cached

LOG = logging.getLogger(__package__)


def tournament_line(t):
    return "{} {} {} {}".format(t["tournament_id"], t["name"], t["location"], t["end_date"])


def list_tournaments(renew_time=3600, force=False):
    """List all naf tournaments from members.thenaf.net"""
    filename = "data/naf_tourneys.html"
    LOG.debug("Listing tournaments")
    last_modified = round((time.time() - os.path.getmtime(filename)))
    LOG.debug("data/naf_tourneys.html modified %ss ago", last_modified)

    if force or last_modified > renew_time:
        LOG.debug("Downloading tournamentlist")
        fetch_tournamentlist.fetch_tournamentlist(target=filename)
    else:
        LOG.info("Using existing tournament data in %s", filename)
        LOG.debug("Skipping download due to last modified %s < %s", last_modified, renew_time)

    tournaments = load_cached(parse_tournamentlist.parse_file, filename)

    return tournaments


def no_data(tournaments):
    tournament_file = "data/tournaments/t{}.html"
    match_file = "data/matches/m{}.html"

    for t in tournaments:
        if not os.path.exists(tournament_file.format(t["tournament_id"])) or not os.path.exists(match_file.format(t["tournament_id"])):
            LOG.info("NO DATA for {}".format(t["tournament_id"]))
            yield t


def future(tournaments):
    today = datetime.datetime.now().isoformat()
    LOG.debug("Filter future tournaments %s", len(tournaments))
    return filter(lambda t: t["end_date"] > today, tournaments)


def past(tournaments):
    today = datetime.datetime.now().isoformat()
    LOG.debug("Filter past tournaments %s", len(tournaments))
    return filter(lambda t: t["end_date"] < today, tournaments)


def no_matches(tournaments):
    result = []
    for t in tournaments:
        matchfile = "data/matches/m{}.html".format(t["tournament_id"])
        matches = load_cached(parse_matches.parse_match, matchfile)
        LOG.debug("Tournament {} {} {} matches".format(t["tournament_id"], t["name"], len(matches)))
        if len(matches) < 1:
            result.append(t)

    return result


def recent(tournaments):
    recently = (datetime.datetime.now() - datetime.timedelta(30)).isoformat()
    today = datetime.datetime.now().isoformat()
    LOG.debug("Filter tournaments from %s tournaments", len(tournaments))
    LOG.debug("Date range %s - %s", today, recently)

    return filter(lambda t: today > t["end_date"] > recently, tournaments)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    tournaments = list_tournaments()
    past_tournaments = list(past(tournaments))
    future_tournaments = list(future(tournaments))
    recent_tournaments = list(recent(tournaments))
    recent_nomatches = list(no_matches(recent_tournaments))
    past_no_match = len(list(no_matches(past_tournaments)))

    print("Found {} tournaments".format(len(tournaments)))
    print("{} are past tournaments".format(len(past_tournaments)))
    print("{} are past tournaments with no matches".format(past_no_match))
    print("{} are future tournaments".format(len(future_tournaments)))
    print("{} are recent tournaments".format(len(recent_tournaments)))
    print("{} are recent tournaments with no matches".format(len(recent_nomatches)))

    if "--recent" in sys.argv:
        print("recent with matches")
        for t in recent_tournaments:
            if t not in recent_nomatches:
                print(tournament_line(t))
        print("recent with no matches")
        for t in recent_nomatches:
            print(tournament_line(t))


if __name__ == "__main__":
    main()