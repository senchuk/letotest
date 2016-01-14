# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Общий класс работы с базами.
# P.S: - Том попал в непростое положение.
#        Однако Крис с пониманием отнесся к тому факту, что в руках у Тома была пара предметов,
#        похожих на заряженные ружья. В свою очередь, Том с пониманием отнесся к другому факту: ружья не были заряжены.
#        Так что, по большому счету, когда Том вышел через черный ход, а Крис ушел с деньгами — никто не потерял лица.
#--------------------------------------------------------------------
from support import service_log, configs
from support.databases.db_cassandra import ClassCassandraDriver
from support.databases.db_elasticsearch import ClassElasticsearchConnections
from support.databases.db_postgresql import ClassPsyCopg2
from support.databases.db_oracle import ClassCxOracle
from support.databases.db_redis import ClassRedis
from support.utils.variables import TVariables
from tests.new_service.dbase_methods.db_new_service import ClassNewApiSql
from tests.new_service.dbase_methods.db_oracle_query import ClassOracleSql

__author__ = 'Strubachev'


class ClassDatabasesWork():

    prefix_databases = "db"
    prefix_nutcracker = "nutcracker"

    # карта сервисов и типов соответствия их с Базами данных
    sv = {"pgsql": {"new_api": [ClassNewApiSql, ClassPsyCopg2]},
          "oraclesql": {"oracle": [ClassOracleSql, ClassCxOracle]},
          "redis": {"<redis>": [None, ClassRedis]},
          "cassandra": {"<cassandra>": [None, ClassCassandraDriver]},
          "elasticsearch": {"<elasticsearch>": [None, ClassElasticsearchConnections]}
          }

    def __init__(self, dbhost=None, dbport=None, dbtype=None, dbname=None, dbuser=None, dbpasswd=None):
        self.params_authentication = {"host": dbhost,
                                      "port": dbport,
                                      "name": dbname,
                                      "user": dbuser,
                                      "passwd": dbpasswd}
        self.dbtype = dbtype

    def __getattr__(self, item):
        if item in self.find_prefixes_connects("db"):
            # для БД
            global prefix_db
            values_authentication = {"dbhost": configs.config["env_info"][item + "_host"],
                                     "dbtype": configs.config["env_info"][item + "_type"],
                                     "dbname": configs.config["env_info"][item + "_name"]}
            # Могут быть необязательные поля
            if item + "_port" in configs.config["env_info"].keys():
                values_authentication.update({"dbport": configs.config["env_info"][item + "_port"]})
            if item + "_passwd" in configs.config["env_info"].keys():
                values_authentication.update({"dbpasswd": configs.config["env_info"][item + "_passwd"]})
            if item + "_login" in configs.config["env_info"]:
                values_authentication.update({"dbuser": configs.config["env_info"][item + "_login"]})

            return ClassDatabasesWork(**values_authentication)

        elif item in self.find_prefixes_connects("nut"):
            from support.utils.nutcracker import ClassNutcracker
            return ClassNutcracker(item)

        elif item in TVariables.thrift.workers:
            # Подключения по типам БД (связка файлов с методами для БД)
            for name_type, service_value in self.sv.iteritems():
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
    def find_prefixes_connects(name="db"):
        """ Найти префиксы для  БД.
        :param name: название префикса для поиска
        :return: список префиксов
        """
        if name == "db":
            prf = ClassDatabasesWork.prefix_databases
        elif name == "nut":
            prf = ClassDatabasesWork.prefix_nutcracker
        bases_val = [key for key in configs.config["env_info"].keys() if key[:len(prf)] == prf]
        prefixes = set([index[:index.find("_")] for index in bases_val])
        return prefixes

    #def import_libs(self):
    #    try:
    #        # Производим динамический импорт сгенериррованных файлов для Thrift
    #        #path = TVariables.accounting.worker
    #        service_log.put("Get path by worker: %s" % path)
    #        get_lib = lambda path_lib: path_lib[path_lib.rfind(".")+1:]
    #        self.worker = __import__(path, fromlist=[get_lib(path)])
    #        service_log.put("Import libs worker: path=%s, name=%s" % (path, get_lib(path)))
    #    except ImportError, tx:
    #        msg_error = "Import lib for worker - %s" % tx
    #        service_log.error(msg_error)
    #        raise AssertionError(msg_error)


databases = ClassDatabasesWork()