#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import argparse
import types
import logging

import nafparser

LOG = logging.getLogger(__package__)


def get_parser_choice(choice):
    LOG.debug('Choices %s', choice)
    if choice == 'coach':
        return nafparser.parse_coach
    if choice == 'tournament':
        return nafparser.parse_tournament
    if choice == 'tournaments' or choice == 'tournamentlist':
        return nafparser.parse_tournaments
    return None


def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if '--debug' in sys.argv else logging.INFO, format=log_format)
    argparser = argparse.ArgumentParser()

    argparser.add_argument('--debug', action='store_true')
    argparser.add_argument('--parser', type=str, choices=['coach', 'matches', 'tournaments', 'tournamentlist', 'tournament'],
                           help='Force selected parser')
    argparser.add_argument('--tournament-list', action='store_true')

    argparser.add_argument('sources', type=str, nargs='+', help='Sources can be (html) filename(s)')

    arguments = argparser.parse_args()
    LOG.debug(arguments)

    parser = get_parser_choice(arguments.parser)
    result = nafparser.parse_all(arguments.sources, parser=parser)

    for parsed in result:
        pprint(parsed, indent=4)


if __name__ == "__main__":
    main()