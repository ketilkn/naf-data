"""
HTML parser for pages on http://members.thenaf.net

This module (nafparser.__init__) covers most of the functionality in the package.
submodules are subject to name changes (2019-10-19)
"""
import os.path
import typing
import bs4
import logging

import nafparser.coach
import nafparser.matches
import nafparser.tournamentlist
import nafparser.tournament

LOG = logging.getLogger(__package__)


def _file_to_soup(filename: str) -> bs4.BeautifulSoup:
    """Load bs4.soup from file"""
    with open(filename, 'r') as f:
        return bs4.BeautifulSoup(f.read(), 'lxml')


def parse_coach(source: str) -> typing.Dict:
    """Parse source:str (filename) as coachpage. Return dict of coach"""
    LOG.debug('Parsing coach from %s', type(source))
    return nafparser.coach.fromfile(source)


def parse_tournament(source: str) -> typing.Dict:
    """Parse source:str (filename) as tournament. Return dict of tournament"""
    LOG.debug('Parsing tournament from %s', type(source))
    return nafparser.tournament.parse_soup(_file_to_soup(source))


def parse_tournaments(source: str) -> typing.List[typing.Dict]:
    """Parse source:str (filename) as tournament list. Return list of limited tournament dicts"""
    LOG.debug('Parsing tournaments from %s', type(source))
    return nafparser.tournamentlist.load2(nafparser.tournamentlist.parse_file, filename=source)


def parse_tournamentmatches(source: str) -> typing.List[typing.Dict]:
    """Parse source:str (filename) as tournament matches. Return List with dicts of matches"""
    LOG.debug('Parsing tournament matches from %s', type(source))
    return nafparser.matches.from_file(source)


def _parse_auto(source: str):
    """Attempts to select the most appropriate parser for the provided source

    Parameters:
    source (str): filename with relative or absolute location

    Returns:
    parsed source (Dict or Source) for the detected type.
    None if no appropriate parser is found
    """
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


def parse(source, parser=_parse_auto):
    """Convenience function that will parse source using provided parser and  return the result.
    If no parser is defined the function will try to guess.

    Parameters:
    source (str): filename with relative or absolute location
    parser (Callable): Function to use for parsing. default = parse_auto

    Returns:
    parsed source (Dict or List)
    """
    use_parser = parser if parser else _parse_auto
    return use_parser(source)


def parse_all(sources: typing.List[str], parser: typing.Callable[[str], typing.Dict] = None) -> typing.Iterator:
    """Convenience function that will parse sources using provided parser and  yields the result.
    If no parser is defined the function will try to guess.

    Parameters:
    sources (List[str] | str): List or string of filenames
    parser (Callable): Function to use for parsing. default = parse_auto

    Returns:
    generator containing parsed sources (Dict or List)
    """
    use_parser = parser if parser else _parse_auto

    source_list = sources if isinstance(sources, list) else [sources]
    for source in source_list:
        yield use_parser(source)

