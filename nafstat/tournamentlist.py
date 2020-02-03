#!/usr/bin/env python
"""  Parse match from HTML """
import datetime
import time
import os
import os.path
import logging
import nafparser
from nafstat import fetch_tournamentlist
from nafstat.file_loader import load_cached
import nafstat.collate

LOG = logging.getLogger(__package__)


def tournament_line(t):
    return "{} {} {} {}".format(t["tournament_id"], t["end_date"], t["name"], t["location"])


def load_tournaments(renew_time=3600, force=False):
    """List all naf tournaments from members.thenaf.net"""
    filename = "data/naf_tourneys.html"
    LOG.debug("Loading tournaments")
    last_modified = round((time.time() - os.path.getmtime(filename)))
    LOG.debug("data/naf_tourneys.html modified %ss ago", last_modified)

    if force or last_modified > renew_time:
        LOG.debug("Downloading tournamentlist")
        fetch_tournamentlist.fetch_tournamentlist(target=filename)
    else:
        LOG.debug("Using existing tournament data in %s", filename)
        LOG.debug("Skipping download due to last modified %s < %s", last_modified, renew_time)

    tournaments = load_cached(nafparser.parse_tournaments, filename)

    return tournaments


def list_tournaments(renew_time=False, force=None):
    """List all naf tournaments from members.thenaf.net"""
    filename = "data/naf_tourneys.html"
    LOG.debug("Listing tournaments")

    if renew_time or force:
        return load_tournaments(renew_time=renew_time, force=force)
    tournaments = load_cached(nafparser.parse_tournaments, filename)

    return tournaments


def no_data(tournaments):
    tournament_file = "data/tournaments/t{}.html"
    match_file = "data/matches/m{}.html"

    for t in tournaments:
        if not os.path.exists(tournament_file.format(t["tournament_id"])) or not os.path.exists(match_file.format(t["tournament_id"])):
            LOG.warning("NO DATA for {}".format(t["tournament_id"]))
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
    for t in load_matches(tournaments):
        if len(t["matches"]) < 1:
            result.append(t)

    return result


def unknown_coaches(tournaments):
    LOG.debug("Searching for tournaments with unknown coaches")
    import nafstat.coachlist
    coaches = set(nafstat.coachlist.load_dict_by_name().keys())
    missing = []
    for t in load_matches(tournaments):
        tournament_coaches = coaches_in_tournament(t)

        missing_in_tournament = tournament_coaches.difference(coaches)
        if missing_in_tournament:
            LOG.debug("Unknown coaches in tournament: %s %s", t["tournament_id"], missing_in_tournament)
            missing.append(t)

    return missing


def load_matches(tournaments):
    for t in tournaments:
        matchfile = "data/matches/m{}.html".format(t["tournament_id"])
        matches = load_cached(nafparser.parse_matches, matchfile)
        LOG.debug("Tournament {} {} {} matches".format(t["tournament_id"], t["name"], len(matches)))
        t["matches"] = matches
        yield t


def recent(tournaments, number_of_days=30):
    recently = (datetime.datetime.now() - datetime.timedelta(number_of_days)).isoformat()
    today = datetime.datetime.now().isoformat()
    LOG.debug("Filter tournaments from %s tournaments", len(tournaments))
    LOG.debug("Date range %s - %s", today, recently)

    return filter(lambda t: today > t["end_date"] > recently, tournaments)


def by_id(tournaments, ids):
    LOG.debug("Filter %s tournaments by id", len(tournaments))

    return filter(lambda t: t["tournament_id"] in ids, tournaments)


def coaches_in_tournament(tournament):
    LOG.debug("All coaches for tournament %s %s", tournament["tournament_id"], tournament["name"])
    coaches = set()
    if "matches" not in tournament:
        LOG.warning("Missing key 'matches' in tournament")
        return coaches

    for m in tournament["matches"]:
        coaches.add(m["home_coach"])
        coaches.add(m["away_coach"])

    LOG.debug("Found %s coaches", len(coaches))
    return coaches


def coaches_by_tournaments(tournaments):
    LOG.debug("Update coaches for %s tournaments", len(tournaments))

    all_coaches = set()
    for t in tournaments:
        tournament = nafstat.collate.load_tournament(t)
        coaches = coaches_in_tournament(tournament)
        all_coaches.update(coaches)

    LOG.debug("Found %s coaches in %s tournaments", len(all_coaches), len(tournaments))
    return all_coaches


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
