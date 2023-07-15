import argparse
import configparser
import csv
import datetime
import json
import logging
import pathlib
import sys
import time

import pymysql
import rich


LOG = logging.getLogger(__package__)


TOURNAMENT_QUERY = """
SELECT nt.tournamentname, nt.tournamentid, nt.tournamentstartdate, nt.tournamentenddate,
    nt.tournamentstyle, nt.tournamentscoring, nt.tournamentorg, 
    nt.tournamentemail, nt.tournamenturl, nt.tournamentinformation,
    nt.tournamentnation, nt.tournamentcity, 
    nts.winnerCoachID, winner.pn_uname as winner_uname,
    nts.runnerUpCoachID, runnerup.pn_uname as runnerup_uname,
    nts.mostTouchdownsCoachID, mosttouchdowns.pn_uname as mosttouchdowns_uname,
    nts.mostCasualitiesCoachID, mostcasualties.pn_uname as mostcasualties_uname,
    nts.stuntyCupCoachID, stuntycup.pn_uname as stuntycup_uname, 
    nts.bestPainterCoachID, bestpainted.pn_uname as bestpainted_uname,
    ntv.variantname, ntv.variantid,
    ntr.rulesetname, ntr.rulesetid,
    count(ng.gameid) as game_count,
    sum(ng.goalshome)+sum(ng.goalsaway) as touchdown_count,
    sum(ng.goalshome)+sum(ng.goalsaway),
    sum(ng.badlyhurthome)+sum(ng.badlyhurtaway)+
    sum(ng.serioushome)+sum(ng.seriousaway)+
    sum(ng.killshome)+sum(ng.killsaway) as casualty_count
FROM naf_tournament nt
LEFT JOIN naf_tournament_statistics nts ON nts.tournamentID=nt.tournamentid
LEFT JOIN naf_variants ntv ON ntv.variantid = nt.naf_variantsid
LEFT JOIN naf_ruleset ntr ON ntr.rulesetid = nt.naf_rulesetid
LEFT JOIN nuke_users winner on winner.pn_uid = nts.winnerCoachID
LEFT JOIN nuke_users runnerup on runnerup.pn_uid = nts.runnerUpCoachID
LEFT JOIN nuke_users stuntycup on stuntycup.pn_uid = nts.stuntyCupCoachID
LEFT JOIN nuke_users mosttouchdowns on mosttouchdowns.pn_uid = nts.mostTouchdownsCoachID
LEFT JOIN nuke_users mostcasualties on mostcasualties.pn_uid = nts.mostCasualitiesCoachID
LEFT JOIN nuke_users bestpainted on bestpainted.pn_uid = nts.bestPainterCoachID
LEFT JOIN naf_game ng on nt.tournamentid=ng.tournamentid
WHERE nt.tournamentstatus='APPROVED' /**AND nts.winnerCoachID > 0**/
GROUP BY nt.tournamentname, nt.tournamentid, nt.tournamentstartdate, nt.tournamentenddate,
    nt.tournamentstyle, nt.tournamentscoring, nt.tournamentorg, 
    nt.tournamentemail, nt.tournamenturl, nt.tournamentinformation,
    nt.tournamentnation, nt.tournamentcity, 
    nts.winnerCoachID, winner.pn_uname ,
    nts.runnerUpCoachID, runnerup.pn_uname ,
    nts.mostTouchdownsCoachID, mosttouchdowns.pn_uname,
    nts.mostCasualitiesCoachID, mostcasualties.pn_uname,
    nts.stuntyCupCoachID, stuntycup.pn_uname, 
    nts.bestPainterCoachID, bestpainted.pn_uname,
    ntv.variantname, ntv.variantid,
    ntr.rulesetname, ntr.rulesetid
"""


def _locate_naf_ini(requested_file):
    if requested_file and requested_file != 'naf.ini':
        return pathlib.Path(requested_file)
    here = pathlib.PosixPath('naf.ini')
    if here.exists():
        return here
    module_parent = pathlib.PosixPath(__file__).parent.parent / 'naf.ini'
    return module_parent


def load_config(config_file='naf.ini', section='nafdata.mysql') -> dict:
    """Load configuration from ini file and return dict"""
    filename = pathlib.PosixPath(_locate_naf_ini(config_file))

    if not filename.exists():
        raise FileNotFoundError('Unable to locate {}'.format(config_file if config_file else filename))

    config = configparser.ConfigParser()
    config.read(filename)

    return config[section]


def create_connection(configuration=None):
    config = configuration or load_config()
    connection = pymysql.connect(host=config.get('host'),
                                 user=config.get('user'),
                                 password=config.get('password'),
                                 database=config.get('database'),
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection


def load_tournaments(connection=None):
    con = connection or create_connection()
    with con.cursor() as cursor:
        query = 'SELECT * FROM naf_tournament'
        cursor.execute(TOURNAMENT_QUERY)
        for row in cursor.fetchall():
            tournament_id = row.get('tournamentid')
            start_date = row.get('tournamentenddate')
            end_date = row.get('tournamentenddate')
            tournament = {
                'name': row.get('tournamentname'),
                'tournament_id': tournament_id,
                'location': row.get('tournamentnation'),
                'start_date': start_date.isoformat() if isinstance(start_date, datetime.date) else None,
                'end_date': end_date.isoformat() if isinstance(end_date, datetime.date) else None,
                'variant': row.get('variantname'),
                'style': row.get('tournamentstyle'),
                'scoring': row.get('tournamentscoring'),
                'type': row.get('tournamenttype'),
                'organizer': row.get('tournamentorg'),
                'email': row.get('tournamentemail'),
                'webpage': row.get('tournamenturl'),
                'information': row.get('tournamentinformation'),
                'nation': row.get('tournamentnation'),
                'city': row.get('tournamentcity'),
                '_last_updated': datetime.datetime.now().isoformat(),
                'awards': {'winner': row.get('winner_uname'),
                           'runner up': row.get('runnerup_uname'),
                           'most touchdowns': row.get('mosttouchdowns_uname'),
                           'most casualties': row.get('mostcasualities_uname'),
                           'stunty cup': row.get('stuntycup_uname'),
                           'best painted': row.get('bestpainted_uname')},
                'other_awards': 'N/A',
                'matches': 'N/A',
                'swiss': 'N/A',
                'ruleset': row.get('rulesetname'),
                'match_count': row.get('game_count'),
                'casualties': int(row.get('casualty_count')) if row.get('casualty_count') else None,
                'touchdowns': int(row.get('touchdown_count')) if row.get('touchdown_count') else None}
            yield tournament


def main():
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.DEBUG if '--debug' in sys.argv else logging.INFO, format=log_format)
    argp = argparse.ArgumentParser()
    argp.add_argument('--debug', action='store_true')
    argp.add_argument('--rich', action='store_true')
    argp.add_argument('--section', type=str, default='nafdata.mysql')
    argp.add_argument('outfile', type=argparse.FileType('w'), nargs='?', default=sys.stdout)
    argp.add_argument('format', type=str, nargs='?', choices=['rich', 'json', 'csv', 'python'], default='rich')

    args = argp.parse_args()

    to_output = []
    csv_writer = None
    with create_connection(load_config(section=args.section)) as connection:
        start_time = time.time()
        for tournament_count, tournament in enumerate(load_tournaments(connection=connection)):
            if args.format == 'rich' or (args.rich and args.outfile == sys.stdout):
                rich.print(tournament)
            if args.format == 'python':
                print(tournament, file=args.outfile)
            elif args.format == 'csv':
                if not csv_writer:
                    csv_writer = csv.DictWriter(args.outfile, fieldnames=tournament.keys())
                    csv_writer.writeheader()
                csv_writer.writerow({k: v for k, v in tournament.items() if k not in ['information']})

            else:
                to_output.append(tournament)
        LOG.debug('Loaded {} tournaments in {} seconds'.format(tournament_count, time.time() - start_time))
        if args.format == 'json':
            json.dump(to_output, args.outfile, ensure_ascii=False)



if __name__ == '__main__':
    main()
