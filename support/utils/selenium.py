# -*- coding: utf-8 -*-
from dbase_methods.db_accounting import ClassAccountingSql
from dbase_methods.db_session import ClassSessionNoSql
from dbase_methods.db_messaging import ClassMessagingNoSql
from dbase_methods.db_warehouse import ClassCassandraCql
from support import service_log, configs
from support.utils.db import ClassDatabasesWork
from support.utils.db_cassandra import ClassCassandraDriver
from support.utils.db_postgresql import ClassPsyCopg2, ClassSaveLinkPostgreSQL
from support.utils.db_redis import ClassRedis
from support.utils.variables import TVariables
__author__ = 's.trubachev'

class ClassSeleniumWork():

    prefix_selenium = "selenium"

    def __init__(self, shost=None, sport=None, sbrowser=None, soptions=None):
        self.params_authentication = {"host": shost,
                                      "port": sport,
                                      "browser": sbrowser,
                                      "options": soptions}

    def __getattr__(self, item):
        if item in self.find_prefixes_databases():
            global prefix_db
            values_connections = {
                "dbhost": configs.config["env_info"][item + "_host"],
                "dbport": configs.config["env_info"][item + "_port"],
                "dbtype": configs.config["env_info"][item + "_type"],
                "dbname": configs.config["env_info"][item + "_name"]}

            # Могут быть необязательные поля
            if item + "_passwd" in configs.config["env_info"].keys():
                values_connections.update({"dbpasswd": configs.config["env_info"][item + "_passwd"]})
            if item + "_login" in configs.config["env_info"]:
                values_connections.update({"dbuser": configs.config["env_info"][item + "_login"]})

            return ClassDatabasesWork(**values_connections)
        elif item in TVariables.thrift.workers:

            # карта сервисов и типов соответствия их с Базами данных
            sv = {"pgsql": {"accounting": [ClassAccountingSql, ClassPsyCopg2]},
                  "redis": {"session": [ClassSessionNoSql, ClassRedis], "messaging": [ClassMessagingNoSql, ClassRedis]},
                  "cassandra": {"warehouse": [ClassCassandraCql, ClassCassandraDriver], }
                  }

            for name_type, service_value in sv.iteritems():
                if self.dbtype == name_type:
                    for name_service, links_service in service_value.iteritems():
                        if item == name_service:
                            return links_service[0](links_service[1](**self.params_authentication).execute)
                    else:
                        msg_error = "Not found class for the work with worker databases."
                        service_log.error(msg_error)
                        raise AssertionError(msg_error)
            else:
                msg_error = "Not detected type database in env.cfg!"
                service_log.error(msg_error)
                raise AssertionError(msg_error)

    @staticmethod
    def find_prefixes_databases():
        bases_val = [key for key in configs.config["env_info"].keys() if key[:2] == ClassDatabasesWork.prefix_selenium]
        prefixes = set([index[:index.find("_")] for index in bases_val])
        if len(prefixes) != 0:
            return prefixes
        else:
            msg_error = "Not found prefix databases!"
            service_log.error(msg_error)
            raise AssertionError(msg_error)


selenium = ClassSeleniumWork()