#!/usr/bin/env python
"""  Parse match from HTML """
import os
import logging
import argparse
import pymysql
from nafstat.dbexport import to_sqlite

LOG = logging.getLogger(__name__)


def create_schema(connection, filename="nafstat/dbexport/schema.sql"):
    LOG.debug("Creating schema from %s", filename)
    os.system("mysql -u {} --password={} {} < {}".format(connection.user.decode(), connection.password.decode(), connection.db.decode(), filename))
    LOG.debug("Schema OK")


def create_index(connection, filename="nafstat/dbexport/index.sql"):
    create_schema(connection, filename)


def create_view(connection, filename="nafstat/dbexport/view.sql"):
    create_schema(connection, filename)


def to_db(schema, username, password):
    LOG.info("Connection to %s", schema)
    connection = pymysql.connect(user=username, password=password, db=schema, charset="utf8mb4")

    LOG.info("Create schema")
    create_schema(connection, filename="nafstat/dbexport/mysql.sql")

    #LOG.info("Create view")
    #create_view(connection)

    LOG.info("Add races")
    to_sqlite.add_races(connection)

    LOG.info("Add coaches")
    to_sqlite.add_coaches(connection)
    connection.commit()

    LOG.info("Add glicko")
    to_sqlite.add_glicko(connection)
    connection.commit()

    LOG.info("Add tournaments")
    to_sqlite.all_tournaments(connection)

    connection.commit()
    connection.close()


def main():
    import sys
    log_format = "[%(levelname)s:%(filename)s:%(lineno)s - %(funcName)20s ] %(message)s"
    logging.basicConfig(level=logging.INFO if "--debug" not in sys.argv else logging.DEBUG, format=log_format)
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("schema")
    argument_parser.add_argument("username")
    argument_parser.add_argument("password")

    arguments = argument_parser.parse_args()

    to_db(schema=arguments.schema, username=arguments.username, password=arguments.password)


if __name__ == "__main__":
    main()
