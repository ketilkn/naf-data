import os.path
import types
import typing
import bs4
import logging

import nafparser.coachparser
import nafparser.matchesparser
import nafparser.tournamentlistparser
import nafparser.tournamentparser

LOG = logging.getLogger(__package__)


def _file_to_soup(filename: str) -> bs4.BeautifulSoup:
    """Load bs4.soup from file"""
    with open(filename, 'r') as f:
        return bs4.BeautifulSoup(f.read(), 'lxml')


def parse_coach(soup: str) -> types.Dict:
    LOG.debug('Parsing coach from %s', type(soup))
    return nafparser.coachparser.fromfile(soup)


def parse_tournament(soup: str) -> types.Dict:
    LOG.debug('Parsing tournament from %s', type(soup))
    return nafparser.tournamentparser.parse_tournament(_file_to_soup(soup))


def parse_tournaments(soup: str) -> typing.List[types.Dict]:
    LOG.debug('Parsing tournaments from %s', type(soup))
    return nafparser.tournamentlistparser.load2(nafparser.tournamentlistparser.parse_file, filename=soup)


def parse_tournamentmatches(soup: str) -> typing.List[types.Dict]:
    LOG.debug('Parsing tournament matches from %s', type(soup))
    return nafparser.matchesparser.from_file(soup)


def parse_auto(soup: str):
    LOG.debug('Parsing auto from %s', type(soup))
    if os.path.isfile(soup):
        if 'coach' in soup:
            return parse_coach(soup)
        if 'tournament' in soup:
            return parse_tournament(soup)
        if 'match' in soup:
            return parse_tournamentmatches(soup)
        if 'tournaments' in soup or 'tourneys' in soup:
            return parse_tournaments(soup)


def parse(source, parser=parse_auto):
    sources = source if isinstance(source, list) else [source]

    for s in sources:
        yield parser(s)

