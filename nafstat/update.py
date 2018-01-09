#!/usr/bin/env python
""" Update nafstat from members.thenaf.net """
import sys
import logging

import session

LOG = logging.getLogger(__package__)


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)


if __name__ == "__main__":
    main()