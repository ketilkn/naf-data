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
import nafstat.collate

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


def update_tournaments(tournaments, throttle=True):
    LOG.debug("Updating %s tournaments", len(tournaments))
    for idx, t in enumerate(tournaments):
        update_tournament(t, throttle)


def coaches_in_tournament(tournament):
    LOG.debug("All coaches for tournament %s %s", tournament["tournament_id"], tournament["name"])
    coaches = set()
    if "matches" not in tournament:
        LOG.warning("Missing key 'matches' in tournament")
        return []

    for m in tournament["matches"]:
        coaches.add(m["home_coach"])
        coaches.add(m["away_coach"])

    LOG.debug("Found %s coaches", len(coaches))
    return coaches


def find_coaches_in_tournaments(tournaments):
    LOG.info("Update coaches for %s tournaments", len(tournaments))

    all_coaches = set()
    for t in tournaments:
        tournament = nafstat.collate.load_tournament(t)
        coaches = coaches_in_tournament(tournament)
        all_coaches.update(coaches)

    LOG.debug("Found %s coaches in %s tournaments", len(all_coaches), len(tournaments))


def update_recent(throttle=True):
    recent_tournaments = list(tournamentlist.recent(tournamentlist.list_tournaments(), 16))
    LOG.info("Found {} recent tournament{}".format(len(recent_tournaments), "s" if len(recent_tournaments) != 1 else ""))

    if recent_tournaments:
        update_tournaments(recent_tournaments, throttle)
        find_coaches_in_tournaments(recent_tournaments)


def update_new(throttle=True):
    new_tournaments = list(tournamentlist.no_data(tournamentlist.list_tournaments()))
    LOG.info("Found {} new tournament{}".format(len(new_tournaments), "s" if len(new_tournaments) != 1 else ""))

    if new_tournaments:
        update_tournaments(new_tournaments, throttle)


def update(throttle=True):
    """ Download recent tournaments from thenaf.net  """
    LOG.info("Updating NAF data")
    if not throttle:
        LOG.warning("No delay between requests")
    else:
        LOG.debug("Politely using delay between requests")

    update_new(throttle)
    update_recent(throttle)


def main():
    import sys
    LOG.info("Update started at %s", datetime.datetime.now().isoformat())
    start = time.time()
    update(throttle="--no-throttle" not in sys.argv)
    LOG.info("Update ended after %s at %s", humanfriendly.format_timespan(time.time() - start), datetime.datetime.now().isoformat())


if __name__ == "__main__":
    main()