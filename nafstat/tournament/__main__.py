#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging
import nafstat.tournament.tournamentlist


LOG = logging.getLogger(__package__)


def main():
    from pprint import pprint
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    for t in nafstat.tournament.tournamentlist.list_tournaments():
        pprint(t, indent=4)



if __name__ == "__main__":
    main()