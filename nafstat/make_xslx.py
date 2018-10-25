#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import copy
import logging
import openpyxl
import shutil

import nafstat.collate
LOG = logging.getLogger(__package__)


def to_xlsx(matches):
    input_file = "template.xlsx"
    output_file = "all_matches.xlsx"
    copy_to = "/home/ketilkn/Dropbox/bloodbowl/nafdata/all_matches.xlsx"
    LOG.info("Opening file %s", input_file)
    columns = ["date", "tournament_id", "match_id", "tournament_name", "home_coach", "home_race", "home_result", "home_score", "away_score", "away_result", "away_race", "away_coach", "casualties?", "home_cas", "away_cas", "mirror", "home_tr", "away_tr", "variant", "swiss", "ruleset", "style", "location", "home_nationality", "away_nationality"]

    LOG.debug("Load workbook")
    workbook = openpyxl.load_workbook(input_file)
    LOG.debug("Load worksheet")
    matchsheet = workbook["all_matches"]

    tournament_name = ""
    for idx, m in enumerate(matches):
        if tournament_name != m["tournament_name"]:
            tournament_name = m["tournament_name"]
            LOG.info("Writing matches for %s %s", m["tournament_id"], tournament_name)
        LOG.debug("Write row %s %s %s %s", idx, m["tmid"], m["home_coach"], m["away_coach"])
        LOG.debug("Write match {} {} {} {}-{} {} {}".format(m['tournament_name'], m['home_coach'], m['home_race'], m['home_score'], m['away_score'], m['away_race'], m['away_coach']))
        row = []
        for column in columns:
            row.append(m[column])

        LOG.debug("Writing row to sheet")
        matchsheet.append(row)
    LOG.info("Wrote %s lines", idx + 1)
    LOG.debug("Update named ranges");
    workbook.get_named_range("AWAY_RACE").attr_text = "all_matches!$K$2:$K${}".format(idx + 2)
    workbook.get_named_range("away_result").attr_text = "all_matches!$J$2:$J${}".format(idx + 2)
    workbook.get_named_range("home_race").attr_text = "all_matches!$F$2:$F${}".format(idx + 2)
    workbook.get_named_range("HOME_RESULT").attr_text = "all_matches!$G$2:$G${}".format(idx + 2)
    workbook.get_named_range("match_date").attr_text = "all_matches!$A$2:$A${}".format(idx + 2)
    workbook.get_named_range("MIRROR_MATCH").attr_text = "all_matches!$P$2:$P${}".format(idx + 2)

    LOG.debug("Finished writing %s", output_file)
    LOG.info("Saving %s", output_file)
    workbook.save(output_file)
    LOG.info("updating target")
    #LOG.debug("copy %s to %s", output_file, copy_to)
    #shutil.copy(output_file, copy_to)


def all_matches():
    for t in nafstat.collate.load_all():
        for m in t["matches"]:
            match = copy.copy(m)
            match["tournament_id"] = t["tournament_id"]
            match["tournament_name"] = t["name"]
            match["tmid"] = "{}#{}".format(t['tournament_id'], m['match_id'].zfill(3))
            match["variant"] = t["variant"]
            match["swiss"] = t["swiss"]
            match["datetime"] = '{} {}'.format(m["date"], m["time"])
            match["tournament_date"] = t["start_date"]
            match["location"] = t["location"]
            match["style"] = t["style"].strip().replace("\n", '').replace("  ", " ")
            match["casualties?"] = t["casualties"]
            match["order"] = "{} {} {}".format(t['start_date'], t['name'], m['match_id'].zfill(4))
            match["mirror"] = m["home_race"].lower() == m["away_race"].lower()
            match["ruleset"] = t["ruleset"] if "unknown" not in t["ruleset"] else ""

            yield match


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if "--debug" in sys.argv else logging.INFO, format=log_format)
    LOG.info("All matches")
    to_xlsx(sorted(all_matches(), key=lambda m: m["order"], reverse=True))


if __name__ == "__main__":
    main()
