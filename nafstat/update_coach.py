#!/usr/bin/env python
"""  Parse match from HTML """
import time
import logging
import humanfriendly
import nafstat.tournament.fetch_coach
LOG = logging.getLogger(__package__)


def update_coach_by_nick(coach_nick, throttle=True):
    LOG.debug("Looking for coach %s", coach_nick)

    start = time.time()
    coach = nafstat.tournament.fetch_coach.fetch_coach_by_nick(coach_nick)
    request_time = time.time() - start
    if throttle:
        LOG.debug("Waiting %s", humanfriendly.format_timespan(request_time))
        time.sleep(request_time)
    else:
        LOG.debug("Throttle is False")
    return coach


def update_coaches_by_nick(coaches_nick, throttle=True):
    LOG.info("Updating %s coaches by nick lookup", len(coaches_nick))
    for idx, coach in enumerate(coaches_nick):
        update_coach_by_nick(coach, throttle)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    update_coaches_by_nick(sys.argv[1:] if len(sys.argv) > 1 else ["joemanji", "straume", "KyRRe"])


if __name__ == "__main__":
    main()