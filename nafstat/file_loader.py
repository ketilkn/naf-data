#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging
import os
import os.path
import json
from bs4 import BeautifulSoup

LOG = logging.getLogger(__package__)


def load_json(filename):
    LOG.debug("load_json %s", filename)
    if not os.path.isfile(filename):
        LOG.error("%s is not a file")
        return {}
    with open(filename) as json_file:
        data = json.load(json_file)
        LOG.debug("Loaded from cache %s", filename)
        return data


def save_json(filename, data):
    LOG.debug("save_json %s %s", filename, len(data))
    if not os.path.isfile(filename):
        with open(filename, "w") as json_file:
            json.dump(data, json_file)


def load_cached(parser, filename="data/naf_tourneys.html"):
    LOG.debug("load_cache %s %s", parser.__name__, filename)
    cache_filename = filename[0:filename.rfind(".")] + ".json"
    LOG.debug("Checking for cache file %s", cache_filename)

    if os.path.exists(filename) and os.path.exists(cache_filename):
        LOG.debug("Checking mtime")
        LOG.debug("file: %s", os.path.getmtime(filename))
        LOG.debug("cache:%s", os.path.getmtime(cache_filename))
        if os.path.getmtime(filename) < os.path.getmtime(cache_filename):
            return load_json(cache_filename)
        else:
            LOG.debug("%s < %s = %s", os.path.getmtime(filename), os.path.getmtime(cache_filename), os.path.getmtime(filename) < os.path.getmtime(cache_filename))
    else:
        LOG.warning("No cache for %s", filename)

    data = load(parser, filename)
    save_json(cache_filename, data)

    return data


def load(parser=None, filename="data/naf_tourneys.html"):
    LOG.info(f"Loading data from {filename}")
    if not os.path.exists(filename):
        LOG.error(f"{filename} does not exist")
        sys.exit("Unrecoverable error")
    if not os.path.isfile(filename):
        LOG.error(f"{filename} is not a file")
        sys.exit("Unrecoverable error")


    with open(filename, "rb") as f:
        LOG.debug("Decode UTF-8")
        try:
            data = f.read().decode("UTF-8")
            LOG.debug("Parsing file using bs4 lxml")
            result = parser(BeautifulSoup(data, "lxml"))
            if result is None:
                LOG.error(f"Parser {parser.__name__} returned None for {filename}")
                return []
            return result
        except UnicodeDecodeError as ex:
            LOG.exception(ex)
            LOG.error(f"Expected character set UTF-8 for input file {filename}")

    return []


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    from . tournament import parse_matches

    result = load_cached(parse_matches.parse_match, "data/matches/m3154.html")
    LOG.info("Loaded %s elements", len(result))
    #print(result)


if __name__ == "__main__":
    main()