#!/usr/bin/env python
"""  Parse match from HTML """
import datetime
import time
import os
import os.path
import logging
from . import fetch_tournamentlist
from . import parse_tournamentlist
from . import parse_matches
from nafstat.file_loader import load_cached

LOG = logging.getLogger(__package__)


def tournament_line(t):
    return "{} {} {} {}".format(t["tournament_id"], t["name"], t["location"], t["end_date"])


def list_tournaments(renew_time = 3600, force = False):
    """List all naf tournaments from members.thenaf.net"""
    LOG.debug("Listing tournaments")
    last_modified = round((time.time() - os.path.getmtime("data/naf_tourneys.html")))
    LOG.debug("data/naf_tourneys.html modified %ss ago", last_modified)

    if (not force and last_modified < renew_time) or fetch_tournamentlist.fetch_tournamentlist():
        return list(parse_tournamentlist.load2(parse_tournamentlist.parse_file))

    return []


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
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    tournaments = list_tournaments()
    past_tournaments = list(past(tournaments))
    future_tournaments = list(future(tournaments))
    recent_tournaments = list(recent(tournaments))
    recent_nomatches = list(no_matches(recent_tournaments))
    LOG.info("Counting tournaments")
    LOG.info("Found %s tournaments", len(tournaments))
    LOG.info("%s are past tournaments", len(past_tournaments))
    #LOG.info("%s are past tournaments with no matches", len(list(no_matches(past_tournaments))))
    LOG.info("%s are future tournaments", len(future_tournaments))
    LOG.info("%s are recent tournaments", len(recent_tournaments))
    LOG.info("%s are recent tournaments with no matches", len(recent_nomatches))

    print("matches")
    for t in recent_tournaments:
        if t not in recent_nomatches:
            print(tournament_line(t))

    print("no matches")
    for t in recent_nomatches:
        print(tournament_line(t))


if __name__ == "__main__":
    main()