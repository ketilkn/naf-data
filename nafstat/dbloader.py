import configparser
import datetime
import pathlib

import pymysql
import rich


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
    ntr.rulesetname, ntr.rulesetid
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


def create_connection():
    config = load_config()
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
            start_date = row.get('tournamentenddate')
            end_date = row.get('tournamentenddate')
            tournament = {
                'name': row.get('tournamentname'),
                'tournament_id': row.get('tournamentid'),
                'location': row.get('tournamentnation'),
                'start_date': start_date,
                'end_date': end_date,
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
                'match_count': 'N/A',
                'casualties': 'N/A',
                'touchdowns': 'N/A',
                'ruleset': row.get('rulesetname')}
            yield tournament


def main():
    for tournament in load_tournaments():
        rich.print(tournament)


if __name__ == '__main__':
    main()
