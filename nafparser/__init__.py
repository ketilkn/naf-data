"""
HTML parser for pages on http://members.thenaf.net

This module (nafparser.__init__) covers most of the functionality in the package.
submodules are subject to name changes (2019-10-19)
"""
import os.path
import typing
import logging

import nafparser.coach
import nafparser.matches
import nafparser.tournamentlist
import nafparser.tournament

LOG = logging.getLogger(__package__)


def _file_to_html(filename: str) -> str:
    """Helper function that read file to text/html

    Parameters:
    filename (str): location of the file

    Returns:
    contents of file as string
    """
    with open(filename, 'r') as f:
        return f.read()


def parse_coach(source: str) -> typing.Dict:
    """Turn the provided HTML source to a dict containing the coach

    Parameters:
    source (str): HTML source

    Returns:
    Dict of coach with
        naf_name: str, naf_number: str, nation: str, ranking: dict(elo, matches, race)
            summary: dict(match_count races_played tournament_count)
    """
    LOG.debug('Parsing coach from %s', type(source))
    return nafparser.coach.parse_html(source)


def parse_tournament(source: str) -> typing.Dict:
    """Turn the provided HTML source to a dict containing tournament data

    Parameters:
    source (str): HTML source

    Returns:
    Dict of tournament with
        name, nation, organizer, awards, other_awards, scoring, style, type, webpage, email, start_date, end_date, information
    """
    LOG.debug('Parsing tournament from %s', type(source))
    return nafparser.tournament.parse_html(source)


def parse_tournaments(source: str) -> typing.List[typing.Dict]:
    """Turn the provided HTML source to a dict containing the tournament list

    Use source from https://member.thenaf.net/index.php?module=NAF&type=tournaments&ordercolumn=tournamentstartdate&showall=1

    Parameters:
    source (str): HTML source

    Returns:
    List of Dict of tournaments with
        name, start_date, location, end_date, variant
    """
    LOG.debug('Parsing tournaments from %s', type(source))
    return nafparser.tournamentlist.parse_html(source)


def parse_tournamentmatches(source: str) -> typing.List[typing.Dict]:
    """Turn the provided HTML source to a dict containing the tournament matches

    Parameters:
    source (str): HTML source

    Returns:
    List of Dict of tournament matches with
        date time match_id
            home_/away_
                coach race score result tr cas bh dead gate
    """
    LOG.debug('Parsing tournament matches from %s', type(source))
    return nafparser.matches.parse_html(source)


def parse_matches(source: str) -> typing.List[typing.Dict]:
    """ Alias for parse_tournamentmatches """
    return parse_tournamentmatches(source)


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
        html_source = _file_to_html(source)
        if 'coach' in source:
            return parse_coach(html_source)
        if 'tournament' in source:
            return parse_tournament(html_source)
        if 'match' in source:
            return parse_tournamentmatches(html_source)
        if 'tournaments' in source or 'tourneys' in source:
            return parse_tournaments(html_source)
    else:
        raise AttributeError


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

    html_source = source
    if os.path.isfile(source):
        html_source = _file_to_html(source)
    return use_parser(html_source)


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

