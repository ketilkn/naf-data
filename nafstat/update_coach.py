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
    import argparse
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("coach", type=str, nargs="*", default=["joemanji", "straume", "KyRRe"],
                                 help="List of coach nicks")

    arguments = argument_parser.parse_args()

    update_coaches_by_nick(arguments.coach)


if __name__ == "__main__":
    main()
