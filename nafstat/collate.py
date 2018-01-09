#!/usr/bin/env python
"""  Parse match from HTML """
import sys
import logging

from nafstat.tournament import parse_tournamentlist, parse_matches, parse_tournament
from .__main__ import load

LOG = logging.getLogger(__package__)


def is_swiss(tourney):
    style = trim(tourney["style"])
    if "swis" in style or "suisse" in style:
        return True
    if "swyss" in style:
        return True
    if "suizo" in style:
        return True

    information = trim(tourney["information"])

    if "swisspair" in information or "swissdraw" in information:
        return True
    if "swisssystem" in information or "swissformat" in information:
        return True
    if "swissstyle" in information:
        return True
    if "swisscombination" in information or "swisspool" in information:
        return True
    if "rondessuisse" in information or "rondesuisse" in information:
        return True
    if "schweizersystem" in information:
        return True
    if "svizzera" in information:
        return True
    if "suizo" in information:
        return True

    return False

def sum_casualties(tourney):
    return sum([int(m["home_cas"]) + int(m["away_cas"]) for m in tourney["matches"]])


def sum_touchdowns(tourney):
    return sum([int(m["home_score"]) + int(m["away_score"]) for m in tourney["matches"]])


def sum_strangeresult(tourney):
    return False


def match_count(tourney):
    return len(tourney["matches"])


def trim(text):
    return "".join(text.split()).lower()


def ruleset(tourney):
    style = trim(tourney["style"])
    information = trim(tourney["information"])

#v5 de Blood Bowl
    if "lrb6" in style or "lrb6" in information:
        return "crp"
    elif "crp" in style or "crp" in information:
        return "crp"
    elif "c.r.p" in information:
        return "crp"
    elif "competitionrulespack" in information:
        return "crp"
    elif "v6debloodbowl" in information:
        return "crp"
    elif "lrb5" in style or "lrb5" in information:
        return "lrb5"
    elif "v5debloodbowl" in information:
        return "lrb5"
    elif "lrb4" in style or "lrb4" in information:
        return "lrb4"
    elif "bb2016" in style or "bb2016" in tourney["information"].lower():
        return "bb2016"

    return "unknown"


def collate_tournament(tourney, tournament_data, matches):
    tourney.update(tournament_data)
    tourney["matches"]=matches
    tourney["swiss"]=is_swiss(tourney)
    tourney["match_count"]=match_count(tourney)
    tourney["casualties"]=sum_casualties(tourney)
    tourney["touchdowns"]=sum_touchdowns(tourney)
    tourney["ruleset"]=ruleset(tourney)
    return tourney


def load_all():
    LOG.debug("loading all tournaments")
    result = []

    for t in load(parse_tournamentlist.parse_file, "data/naf_tourneys.html"):
        LOG.info(f"Loading {t['tournament_id']} {t['name']}")
        LOG.debug(f"Loading data for {t['tournament_id']}")
        tourney_data = load(parse_tournament.parse_tournament, f"data/tournaments/t{t['tournament_id']}.html")
        LOG.debug(f"Loading matches for {t['tournament_id']}")
        match_data = load(parse_matches.parse_match, f"data/matches/m{t['tournament_id']}.html")
        yield collate_tournament(t, tourney_data, match_data)

    return result


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.WARNING, format=log_format)

    do_print = False if "--no-print" in sys.argv else True
    if not do_print:
        del(sys.argv[sys.argv.index("--no-print")])

    printables = False if do_print and len(sys.argv) == 1 else sys.argv[1:]

    stats = {"all": [],
             "no matches": [],
             "no casualties": [],
             "no touchdowns": [],
             "no style": [],
             "no information": [],
             "crp": [],
             "lrb5": [],
             "lrb4": [],
             "bb2016": [],
             "unknown": [],
             "swiss": []}

    for t in load_all():
        stats["all"].append(t["tournament_id"])
        if not t["match_count"]:
            stats["no matches"].append(t["tournament_id"])
            #print(f"Skipping tournament {t['tournament_id']} with no matches")
            continue
        if not t["casualties"]:
            stats["no casualties"].append(t["tournament_id"])
            #print("NO CASUALTIES RECORDED")
        if not t["touchdowns"]:
            stats["no touchdowns"].append(t["tournament_id"])
            if do_print:
                print(f'\n{t["tournament_id"]} {t["ruleset"]} {t["name"]} {t["swiss"]} {t["end_date"]}')
                print("NO TOUCHDOWNS RECORDED")
        if not t["swiss"]:
            if do_print:
                print(f'\n{t["tournament_id"]} {t["ruleset"]} {t["name"]} {t["swiss"]} {t["end_date"]}')
            stats["swiss"].append(t["tournament_id"])
            if do_print:
                print(f'STYLE:\n{t["style"]}')
                print(f'INFORMATION:\n{t["information"]}')
                print("==========================\n")

        stats[t["ruleset"]].append(t["tournament_id"])

    for key, value in stats.items():
        print(f"{key}: {len(value)}")
        if key != "all" and "no " not in key:
            print(value)

    #if do_print:
        #for t in result:
            #if not printables or t["tournament_id"] in printables:
                #pprint(t, indent=2)




if __name__ == "__main__":
    main()