# -*- coding: utf-8 -*-
__author__ = 'Strubachev'
import atexit
import MySQLdb as mdb
from support import configs, logger


class DB:
    connection = None

    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self, host=configs["env_info"]["db_host"],
                user=configs["env_info"]["db_login"],
                passwd=configs["env_info"]["db_passwd"]):
        """
          Try to set up a database connection
          return connection
        """
        self.connection = mdb.connect(host=host,
                                      user=user,
                                      passwd=passwd,
                                      db=configs["env_info"][self.db_name],
                                      charset='utf8')
        self.connection.autocommit(True)

    def query(self, sql):
        """
        Make a sql query
        Return cursor
        If first try failed make the second one
        :param sql: sql query to run
        """
        if not self.connection:
            self.connect()

        try:
            cursor = self._make_query(sql)
        except (AttributeError, mdb.OperationalError):
            logger.error("Could connect to DB. Retrying")
            self.connect()
            cursor = self._make_query(sql)
        return cursor

    def _make_query(self, sql):
        """
        internal function. Make query without an exception catching
        return cursor
        """
        cursor = self.connection.cursor(mdb.cursors.DictCursor)
        cursor.execute(sql)
        return cursor

    def close_connection(self):
        """
        Close connection DB if exist
        """
        if self.connection:
            self.connection.close()


@atexit.register
def close_connections():
    logger.info("Closing opened mysql connections")
    accessible_db.close_connection()


# Make connections to known databases
accessible_db = DB("db_name")
