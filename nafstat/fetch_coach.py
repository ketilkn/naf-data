#!/usr/bin/env python
"""  Parse match from HTML """
import logging
import requests
<<<<<<< HEAD:nafstat/tournament/fetch_coach.py
from nafstat.tournament import fetch_tournamentlist
import nafstat.file_loader
import nafstat.tournament.parse_coach
from nafstat import session
=======
from nafstat import fetch_tournamentlist
import nafparser
>>>>>>> adb6053ad126f405f19d915c17f05c47e82cd6a2:nafstat/fetch_coach.py
import bs4

LOG = logging.getLogger(__package__)

DEFAULT_TARGET = "data/coach/c{}.html"
COACH_URL = "https://member.thenaf.net/index.php?module=NAF&type=coachpage&coach={}"
SEARCH_URL = 'https://member.thenaf.net/index.php?module=NAF&type=tournamentinfo'
<<<<<<< HEAD:nafstat/tournament/fetch_coach.py
=======

>>>>>>> adb6053ad126f405f19d915c17f05c47e82cd6a2:nafstat/fetch_coach.py

def fetch_coach(coach_id, url=COACH_URL, target=DEFAULT_TARGET):
    LOG.debug("fetch_coach %s", coach_id)
    result = fetch_tournamentlist.fetch_tournamentlist(url=COACH_URL.format(coach_id), target=target.format(coach_id))
    return result


def fetch_coach_html_by_nick(coach_id, url=COACH_URL, target=None):
    LOG.debug("fetch_coach_by_nick %s", coach_id)

<<<<<<< HEAD:nafstat/tournament/fetch_coach.py
    response = requests.post(SEARCH_URL, headers=session.build_header(), data={'uname': coach_id})
    if not response.history and response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        el = soup.find(lambda t: t!=None and t.name =='a' and 'coachpage for ' in t.text)
        if el:
            return fetch_coach(el['href'].replace('https://member.thenaf.net/index.php?module=NAF&type=coachpage&coach=', ''))
        #html = response.text
        #return html
    else:
        LOG.warning("Response %s %s for %s", response.status_code, response.reason, SEARCH_URL.format(coach_id))
        LOG.warning(session.build_header())

=======
    response = requests.post(SEARCH_URL, data={'uname': coach_id})
    if not response.history and response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'lxml')
        el = soup.find(lambda t: t!=None and t.name == 'a' and 'coachpage for ' in t.text)
        if el:
            return fetch_coach(
                el['href'].replace('https://member.thenaf.net/index.php?module=NAF&type=coachpage&coach=', ''))
    else:
        LOG.warning("Response %s %s for %s", response.status_code, response.reason, SEARCH_URL)
>>>>>>> adb6053ad126f405f19d915c17f05c47e82cd6a2:nafstat/fetch_coach.py
    return False


def save_coach_by_nick(coach_id, url=COACH_URL, target=None):
    coach, html = fetch_coach_by_nick(coach_id, url, return_html=True)

    if coach and "naf_number" in coach:
        LOG.debug("Naf number is %s", coach["naf_number"])
        LOG.debug("Naf name is %s", coach["naf_name"])

        filename = target if target else DEFAULT_TARGET.format(coach["naf_number"])
        LOG.debug("Open file %s for writing", filename)
        with open(filename, "w") as coach_file:
            coach_file.write(html)
            return filename


def fetch_coach_by_nick(coach_id, url=COACH_URL, target=None, return_html=False):
    LOG.debug("fetch_coach_by_nick %s", coach_id)

    html = fetch_coach_html_by_nick(coach_id, url)
    if html:
        coach = nafparser.parse_coach(html)
        if return_html:
            return coach, html
        return coach

    if return_html:
        return False, False
    return False


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    import sys

    coach_to_find = sys.argv[1] if len(sys.argv) > 1 else "12403"

    if coach_to_find.isdigit():
        fetch_coach(coach_to_find, COACH_URL.format(coach_to_find))
    else:
        html = fetch_coach_html_by_nick(coach_to_find, COACH_URL.format(coach_to_find))
        if html:
            coach = nafparser.parse_coach(html)
            if coach:
                print(coach)


if __name__ == "__main__":
    main()
