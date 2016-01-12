# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Работа с cassandra-driver.
#     https://pypi.python.org/pypi/cassandra-driver/2.1.0
# P.S:  slap shit together and deploy.
#--------------------------------------------------------------------

from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from support import service_log

__author__ = 's.trubachev'


def execute_cql(func):
    """ Обертка для исполнения сql-запросов.
    :type func: __builtin__.function
    :return: ссылка на функцию, с уже исполненым сql-запросом
    """
    def modify(*args, **kwargs):
        params_funct = func(*args, **kwargs)
        ex = args[0].__dict__["func"]
        service_log.put("CQL-query: %s" % str(params_funct))
        if isinstance(params_funct, tuple):
            # если передали несколько параметров к методу
            result = ex(*params_funct)
        else:
            result = ex(params_funct)
        service_log.put("CQL-query result: %s" % result)
        return result
    return modify


class ClassSaveLinkCassandra():
    """
    Класс прородитель для хранения ссылки на функцию испольнения запросов.
    """
    def __init__(self, func):
        self.func = func


class ClassCassandraDriver():
    """
    Класс работы с CassandraDriver.
    """

    def __init__(self, host, port, name, user, passwd):
        # параметры аутетификации к БД
        self.host = map(lambda x: x.strip(), host[1:-1].split(','))  # может храниться массив хостов, str->list
        self.port = int(port)
        self.name = name
        self.user = user
        self.passwd = passwd

        # параметры для работы внутри БД
        self.cluster = None

    def connect_plain_auth(self, user_name, password, port, key_space, contacts_point):
        """ Аутентификация cassandra через имя и пароль.
        :param user_name: имя пользователя
        :param password: пароль пользователя
        :return: ссылка на сессию
        """

        try:
            service_log.put("Create obj PlainTextAuthProvider for cassandra.")
            auth_provider = PlainTextAuthProvider(username=user_name, password=password)
            service_log.put("Create cluster for cassandra.")
            self.cluster = Cluster(contact_points=contacts_point, port=port, auth_provider=auth_provider)
            service_log.put("Create connect with cassandra.")
            session = self.cluster.connect(keyspace=key_space)
            service_log.put("Create session for cluster cassandra.")
            return session
        except Exception, tx:
            msg_error = "Connect with casandra not success!"
            service_log.error(msg_error)
            service_log.error("%s" % str(tx))
            raise msg_error

    def disconnect_all(self):
        """ Дисконнект всех открытых сессий.
        """
        service_log.put("Disconnect all sessions cassandra.")
        self.cluster.shutdown()

    @staticmethod
    def disconnect(session):
        """ Дисконнект для текущей сессий.
        :param session: ссылка на сессию
        """
        service_log.put("Disconnect this session cassandra.")
        session.shutdown()

    def execute(self, req, parameters=None):
        """ Выполнить запрос.
        :param req: сql-запрос
        :return: результат операции
        """

        session = None
        try:
            session = self.connect_plain_auth(user_name=self.user, password=self.passwd, port=self.port,
                                              key_space=self.name, contacts_point=self.host)
            if parameters is not None:
                # вариант с предварительной привязкой параметров, для работы с BLOB
                prepare_params = session.prepare(req)
                bound_params = prepare_params.bind(parameters)
                result = session.execute(bound_params)
            else:
                result = session.execute(req)
            service_log.put("Response from cassandra.")
            if isinstance(result, list):
                if len(result) > 0:
                    return [dict(index.__dict__) for index in result]
                else:
                    return None
            else:
                return result
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            # self.disconnect(session) # закрываем текущую сессию
            self.disconnect_all()   # закрываемся все сессии
