import os.path
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


def parse_coach(source: str) -> typing.Dict:
    LOG.debug('Parsing coach from %s', type(source))
    return nafparser.coachparser.fromfile(source)


def parse_tournament(source: str) -> typing.Dict:
    LOG.debug('Parsing tournament from %s', type(source))
    return nafparser.tournamentparser.parse_tournament(_file_to_soup(source))


def parse_tournaments(source: str) -> typing.List[typing.Dict]:
    LOG.debug('Parsing tournaments from %s', type(source))
    return nafparser.tournamentlistparser.load2(nafparser.tournamentlistparser.parse_file, filename=source)


def parse_tournamentmatches(source: str) -> typing.List[typing.Dict]:
    LOG.debug('Parsing tournament matches from %s', type(source))
    return nafparser.matchesparser.from_file(source)


def parse_auto(source: str):
    LOG.debug('Parsing auto from %s', type(source))
    if os.path.isfile(source):
        if 'coach' in source:
            return parse_coach(source)
        if 'tournament' in source:
            return parse_tournament(source)
        if 'match' in source:
            return parse_tournamentmatches(source)
        if 'tournaments' in source or 'tourneys' in source:
            return parse_tournaments(source)


def parse(source, parser=parse_auto):
    sources = source if isinstance(source, list) else [source]

    for s in sources:
        yield parser(s)

