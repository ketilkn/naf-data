#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import os.path
import time
import logging

import nafstat.session

LOG = logging.getLogger(__package__)
TOURNAMENT_LIST_URL = "https://member.thenaf.net/index.php?module=NAF&type=tournaments&ordercolumn=tournamentstartdate&showall=1"
DEFAULT_TARGET = "data/naf_tourneys.html"


def fetch_tournamentlist(url = TOURNAMENT_LIST_URL, target = DEFAULT_TARGET):
    return fetch_url(url, target, True)


def fetch_url(url, target, returnFile = False):
    if not url:
        LOG.error("url is %s", url)
        sys.exit(1)
    if not url:
        LOG.error("target is %s", url)
        sys.exit(1)
    LOG.debug("Downloading %s %s", target, "(default)" if url == TOURNAMENT_LIST_URL else "")
    LOG.debug("to %s %s", target, "(default)" if target == DEFAULT_TARGET else "")

    path = os.path.dirname(target)
    if not os.path.exists(path):
        LOG.error("Target path %s does not exist")
        sys.exit(2)
        return False

    LOG.debug("target %s is directory %s", path, os.path.isdir(path))
    LOG.debug("target file %s exist %s", target, os.path.isfile(target))

    start_time = time.time()
    download_session = nafstat.session.new_session()
    result = nafstat.session.download_to(download_session, url, target)
    LOG.debug("download_to returned %s in %s ms", result, round((time.time()-start_time)*1000))

    if returnFile:
        with open(target, "rb") as target_file:
            return target_file.read().decode(encoding="UTF-8")

    return result


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)

    result = fetch_tournamentlist(TOURNAMENT_LIST_URL, DEFAULT_TARGET)

    print(result)


if __name__ == "__main__":
    main()