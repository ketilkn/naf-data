#!/usr/bin/env python
"""  Parse match from HTML """
import time
import logging
import humanfriendly
from tqdm import tqdm
import nafstat.tournament.fetch_coach
from nafstat.session import throttle_by_request_time
LOG = logging.getLogger(__package__)


@throttle_by_request_time
def update_coach_by_nick(coach_nick):
    LOG.debug("Looking for coach %s", coach_nick)

    coach = nafstat.tournament.fetch_coach.fetch_coach_by_nick(coach_nick)
    if not coach:
        LOG.warning("Coach with nick %s not found", coach_nick)
    return coach


def update_coaches_by_nick(coaches_nick):
    LOG.info("Updating %s coaches searching for coach_nick", len(coaches_nick))
    for idx, coach in enumerate(tqdm(coaches_nick)):
        update_coach_by_nick(coach)


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    update_coaches_by_nick(sys.argv[1:] if len(sys.argv) > 1 else ["joemanji", "straume", "KyRRe"])


if __name__ == "__main__":
    main()
