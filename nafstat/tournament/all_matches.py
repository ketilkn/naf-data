#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import copy
import logging

import csv

import nafstat.collate.load_all
LOG = logging.getLogger(__package__)


def to_csv(matches):
    LOG.debug(f"Opening file all_matches.csv")
    with open('all_matches.csv', 'w') as csvfile:
        columns = ["date",
                   "tournament_id",
                   "match_id",
                   "tournament_name",
                   "home_coach",
                   "home_race",
                   "home_result",
                   "home_score",
                   "away_score",
                   "away_result",
                   "away_race",
                   "away_coach",
                   "casualties?",
                   "home_cas",
                   "away_cas",
                   "mirror",
                   "home_tr",
                   "away_tr",
                   "variant",
                   "swiss",
                   "ruleset",
                   "style",
                   "location"]
        csv_writer = csv.DictWriter(csvfile, fieldnames=columns, extrasaction='ignore', quotechar='"')
        LOG.debug("Write header")
        csv_writer.writeheader()
        for m in matches:
            LOG.info(f"Write match {m['tournament_name']} {m['home_coach']} {m['home_race']} {m['home_score']}-{m['away_score']} {m['away_race']} {m['away_coach']}")
            csv_writer.writerow(m)
    LOG.debug(f"Finished writing all_matches.csv")



def all_matches():
    for t in nafstat.collate.load_all():
        for m in t["matches"]:
            match = copy.copy(m)
            match["tournament_id"] = t["tournament_id"]
            match["tournament_name"] = t["name"]
            match["tmid"] = f"{t['tournament_id']}#{m['match_id'].zfill(3)}"
            match["variant"] = t["variant"]
            match["swiss"] = t["swiss"]
            match["datetime"] = f'{m["date"]} {m["time"]}'
            match["tournament_date"] = t["start_date"]
            match["location"] = t["location"]
            match["style"] = t["style"].strip().replace("\n", '').replace("  ", " ")
            match["casualties?"] = t["casualties"]
            match["order"] = f"{t['start_date']} {t['name']} {m['match_id'].zfill(4)}"
            match["mirror"] = m["home_race"].lower() == m["away_race"].lower()
            match["ruleset"] = t["ruleset"] if "unknown" not in t["ruleset"] else ""
            yield match



def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_format)
    LOG.info("All matches")
    to_csv(sorted(all_matches(), key=lambda m: m["order"]))



if __name__ == "__main__":
    main()