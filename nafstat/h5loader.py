#!/usr/bin/env python3
"""  Test loading h5"""
from collections import namedtuple
from typing import NamedTuple
from numpy import float64
import datetime
import argparse
import logging.config
from pprint import pprint as pp
import h5py
import numpy as np
import nafstat.races
import nafstat.update
import nafstat.export

logging.config.fileConfig('pylogging.conf', disable_existing_loggers=True)
LOG = logging.getLogger("nafstat")
logging.getLogger("nafstat.file_loader").setLevel(logging.INFO)


class GlickoRank(NamedTuple):
    coach: str
    race: nafstat.races.Race
    period: datetime.date
    mu: float64
    phi: float64


def run_with_arguments(arguments: argparse):
    import tqdm
    LOG.info(arguments)
    ranking = load_file(filename=arguments.filename)

    coach = load_coach(ranking, arguments.coach)
    pp(coach)
    pp(type(coach['phi']))
    pp(type(coach['mu']))
    races = load_races(ranking)
    pp(races)
    race_index = nafstat.races.race_dict()
    race_list = [race_index[r.decode('utf-8')] for r in ranking['race_ids']]
    pp(race_list)
    print('Loading all')
    coach_count = 0
    rank_count = 0
    for c in tqdm.tqdm(load_all_coach_ranks(ranking), total=len(ranking['coaches'])):
        coach_count = coach_count + 1
        tqdm.tqdm.write("{}".format(rank_count))
        for r in c:
            rank_count = rank_count + 1
            #tqdm.tqdm.write('{}'.format(r))
    print('All done ', rank_count)
    #for r in load_coach_ranks(ranking, 'kyrre'):
        #pp(r)

    return ranking


def load_races(ranking: h5py.File):
    return [r.decode('UTF-8') for r in ranking['race_ids']]


def load_all_coach_ranks(ranking: h5py.File):
    for coach in ranking['coaches'].keys():
        yield load_coach_ranks(ranking, coach)


def load_coach_ranks(ranking: h5py.File, coach_nick:str):
    coach = load_coach(ranking, coach_nick)

    for mus, phis, period in zip(coach['mu'], coach['phi'], ranking['date']):
        if all(np.isnan(mus)):
            break
        for mu, phi, race in zip(mus, phis, ranking.get('race_ids')):
            if not np.isnan(mu):
                yield (coach_nick, nafstat.races.RACES.by_race[race.decode('utf-8')].race_id, mu, phi, period, )
                #yield GlickoRank(coach=coach_nick,
                                 #race=nafstat.races.RACES.by_race[race.decode('utf-8')],
                                 #mu=mu, phi=phi,
                                 #period=period)


def load_coach(ranking: h5py.File, coach):
    coach = ranking.get("coaches/{}".format(coach))
    return {'coach': coach,
            'mu': coach['mu'],
            'phi': coach['phi']}


def load_file(filename: str):
    LOG.debug('Loading %s', filename)
    return h5py.File(filename, 'r')


def main():
    import sys
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument('--debug', action='store_true')
    argument_parser.add_argument('filename', nargs='?', default='data/rankings.h5')
    argument_parser.add_argument('--coach', nargs='?', default='Kyrre')

    arguments = argument_parser.parse_args()
    return run_with_arguments(arguments)

ranking = None
if __name__ == "__main__":
    ranking = main()
