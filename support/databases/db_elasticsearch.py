# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Работа с elasticsearch.
#--------------------------------------------------------------------
from elasticsearch import Elasticsearch
from support import service_log

__author__ = 's.trubachev'


def execute_query(func):
    """ Обертка для исполнения elasticsearch-запросов.
    :type func: __builtin__.function
    :return: ссылка на функцию, с уже исполненым elasticsearch-запросом
    """
    def modify(*args, **kwargs):
        params_funct = func(*args, **kwargs)
        ex = args[0].__dict__["func"]
        service_log.put("elasticsearch-query: %s" % str(params_funct))
        if isinstance(params_funct, tuple):
            # если передали несколько параметров к методу
            result = ex(*params_funct)
        else:
            result = ex(params_funct)
        service_log.put("elasticsearch-query result: %s" % result)
        return result
    return modify


class ClassSaveLinkElasticsearch():
    """
    Класс прородитель для хранения ссылки на функцию испольнения запросов.
    """
    def __init__(self, func):
        self.func = func


class ClassElasticsearchConnections():
    """
    Класс работы с Elasticsearch.
    """

    def __init__(self, host, port, name, user, passwd):
        # параметры аутетификации к БД
        self.host = host
        self.port = int(port) if port is not None else None
        self.name = name
        self.user = user
        self.passwd = passwd

        # параметры для работы внутри БД
        self.cluster = None

    @staticmethod
    def connect(hosts):
        es = Elasticsearch(hosts=hosts)
        service_log.put("Connection with Elasticsearch: %s" % str(es))
        return es

    @staticmethod
    def disconnect():
        """ Завершение работы с Elasticsearch.
        :return: None
        """
        service_log.put("End work with Elasticsearch.")
        return None

    def execute(self, req, parameters=None):
        """ Выполнить запрос.
        :param req: сql-запрос
        :return: результат операции
        """

        try:
            result = None
            connection_elastic = self.connect(hosts=self.host)
            if parameters is not None:
                # result = connection_elastic.execute()
                # TODO: параметризированный запуск
                pass
            else:
                result = connection_elastic.search(index=self.name, body=req)
            service_log.put("Response from Elasticsearch.")
            return result
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            self.disconnect()   # завершаем работу
