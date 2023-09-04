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
    nt.tournamentstyle, nt.tournamentscoring, nt.tournamentmajor, nt.tournamentorg, nt.tournamenttype,
    nt.tournamentemail, nt.tournamenturl, nt.tournamentinformation,
    nt.tournamentnation, nt.tournamentcity, 
    nts.awards,
    ntv.variantname, ntv.variantid,
    ntr.rulesetname, ntr.rulesetid,
    count(ng.gameid) as game_count,
    sum(ng.goalshome)+sum(ng.goalsaway) as touchdown_count,
    sum(ng.goalshome)+sum(ng.goalsaway),
    sum(ng.badlyhurthome)+sum(ng.badlyhurtaway)+
    sum(ng.serioushome)+sum(ng.seriousaway)+
    sum(ng.killshome)+sum(ng.killsaway) as casualty_count
FROM naf_tournament nt
LEFT JOIN (
SELECT ntsg.tournamentID, group_concat(concat(ntsl.label,'=',ntsg.coachID,';', replace(replace(nu.pn_uname, ';',''), ',','_'))) as awards
FROM naf_tournament_statistics_group ntsg
JOIN naf_tournament_statistics_list ntsl ON ntsg.typeID=ntsl.id
LEFT JOIN nuke_users nu ON ntsg.coachID=nu.pn_uid
GROUP BY ntsg.tournamentID
) as nts ON nts.tournamentID=nt.tournamentid
LEFT JOIN naf_variants ntv ON ntv.variantid = nt.naf_variantsid
LEFT JOIN naf_ruleset ntr ON ntr.rulesetid = nt.naf_rulesetid
LEFT JOIN naf_game ng on nt.tournamentid=ng.tournamentid
WHERE nt.tournamentstatus='APPROVED' /**AND nts.winnerCoachID > 0**/ /*TOURNAMENT_IDS*/
GROUP BY nt.tournamentname, nt.tournamentid, nt.tournamentstartdate, nt.tournamentenddate,
    nt.tournamentstyle, nt.tournamentscoring, nt.tournamentmajor, nt.tournamentorg, 
    nt.tournamentemail, nt.tournamenturl, nt.tournamentinformation,
    nt.tournamentnation, nt.tournamentcity, 
    nts.awards,
    ntv.variantname, ntv.variantid,
    ntr.rulesetname, ntr.rulesetid
"""


GAME_QUERY = """
SELECT gameid, seasonid, tournamentid, `date`,`hour`,
    homecoachid, racehome, nuh.pn_uname homecoach, goalshome,
    goalsaway, nua.pn_uname as awaycoach, raceaway, awaycoachid, 
    trhome, traway, rephome, repaway, rephome_calibrated, repaway_calibrated,
    badlyhurthome, badlyhurtaway,
    serioushome, seriousaway,
    killshome, killsaway,
    gate,
    winningshome, winningsaway,
    newdate,
    naf_variantsid
FROM thenafne_main.naf_game ng
JOIN thenafne_main.nuke_users nuh on nuh.pn_uid=ng.homecoachid
JOIN thenafne_main.nuke_users nua on nua.pn_uid=ng.awaycoachid
/*WHERE*/
ORDER BY `date`, `hour`, gameid
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


def load_games(tournament_ids, connection=None):
    con = connection or create_connection()
    with con.cursor() as cursor:
        query = GAME_QUERY
        tournaments = [tournament_ids] if isinstance(tournament_ids, int) else tournament_ids
        if tournament_ids:
            query = GAME_QUERY.replace(
                '/*WHERE*/',
                f' AND ng.tournamentid in ({", ".join([str(tid) for tid in tournaments])})')

        cursor.execute(query)
        for game_count, row in enumerate(cursor.fetchall(), start=1):
            game_id = row.get('gameid')
            yield {
        'game_id': game_id,
        "away_tr": row.get('traway'),
        "date": row.get('date'),
        "round": f"{row.get('hour'):02}:00",
        "home_dead": row.get('killshome'),
        "gate": row.get('gate'),
        "away_coach": row.get('awaycoach'),
        "away_coachid": row.get('awaycoachid'),
        "home_race": row.get('racehome'),
        "home_si": row.get('serioushome'),
        "home_tr": row.get('trhome'),
        "home_bh": row.get('badlyhurthome'),
        "time": f'{row.get("hour"):02}:00',
        "home_coach": row.get('homecoach'),
        "home_coachid": row.get('homecoachid'),
        "away_score": row.get('goalsaway'),
        "away_si": row.get('serioushome'),
        "home_score": row.get('goalshome'),
        "match_id": game_count,
        "away_race": row.get('raceaway'),
        "away_bh": row.get('badlyhurtaway'),
        "away_dead": row.get('killsaway')
      }


def load_tournaments(tournament_ids=None, connection=None):
    con = connection or create_connection()
    with con.cursor() as cursor:
        query = TOURNAMENT_QUERY
        if tournament_ids:
            query = TOURNAMENT_QUERY.replace(
                '/*TOURNAMENT_IDS*/',
                f' AND nt.tournamentid in ({", ".join([str(tid) for tid in tournament_ids])}) ')

        cursor.execute(query)
        for row in cursor.fetchall():
            tournament_id = row.get('tournamentid')
            start_date = row.get('tournamentenddate')
            end_date = row.get('tournamentenddate')
            awards = {}
            if row.get('awards'):
                row_awards = row.get('awards')
                awards = {award.split('=', 1)[0].lower():award.split('=', 1)[1].split(';')[-1] for award in row_awards.split(',')}
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
                'major': 1 if 'yes' in row.get('tournamentmajor') else 0,
                'organizer': row.get('tournamentorg'),
                'email': row.get('tournamentemail'),
                'webpage': row.get('tournamenturl'),
                'information': row.get('tournamentinformation'),
                'nation': row.get('tournamentnation'),
                'city': row.get('tournamentcity'),
                '_last_updated': datetime.datetime.now().isoformat(),
                'awards': awards,
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
    argp.add_argument('--tournaments', type=int, nargs='*', default=[])
    argp.add_argument('--config-section', '--section', type=str, default='nafdata.mysql')
    argp.add_argument('outfile', type=argparse.FileType('w'), nargs='?', default=sys.stdout)
    argp.add_argument('format', type=str, nargs='?', choices=['rich', 'json', 'csv', 'python'], default='rich')

    args = argp.parse_args()

    to_output = []
    csv_writer = None
    with create_connection(load_config(section=args.config_section)) as connection:
        start_time = time.time()
        for tournament_count, tournament in enumerate(load_tournaments(tournament_ids=args.tournaments, connection=connection)):
            games = load_games(tournament_ids=[tournament.get('tournament_id')])
            tournament['matches'] = list(games)
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
