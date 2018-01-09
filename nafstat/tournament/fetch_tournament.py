#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging

LOG = logging.getLogger(__package__)
TOURNAMENT_URL = "https://member.thenaf.net/index.php?module=NAF&type=tournaments&func=view&id={}"



def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)


if __name__ == "__main__":
    main()