# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Классы и методы для работы с БД no-sql Redis.
# P.S: Есть многое на свете, друг Горацио! Что и не снилось нашим мудрецам! (c) Гамлет
#--------------------------------------------------------------------
import funcy
import redis
from support import service_log

__author__ = 's.trubachev'


def execute_nosql(func):
    """ Обертка для исполнения nosql-запросов.
    :type func: __builtin__.function
    :return: ссылка на функцию, с уже исполненым sql-запросом
    """
    def modify(*args, **kwargs):
        params_funct = func(*args, **kwargs)
        ex = args[0].__dict__["func"]
        service_log.put("NoSQL-query: %s" % str(params_funct))
        result = None

        if type(params_funct) is dict:
            result = ex(params_funct)

        service_log.put("NoSQL-query result: %s" % result)
        return result
    return modify


class ClassSaveLinkRedis():
    """
    Класс прородитель для хранения ссылки на функцию испольнения запросов.
    """

    @execute_nosql
    def get_hashtable(self, key_name):
        """ Получить все данные ключа.
        :param key_name: hash-номер или имя
        :return: значение ключа
        """
        return dict(type="hgetall", name=key_name)

    @execute_nosql
    def check_exists(self, key_name):
        """ Проверить существование ключа.
        :param key_name: hash-номер или имя
        :return: True или False
        """
        return dict(type="exists", name=key_name)


    @execute_nosql
    def get_field(self, key_table_name, name_field):
        """ Получить поле таблицы ключа.
        :param key_table_name: hash-номер или имя
        :return: значение ключа
        """
        return dict(type="hget", name=key_table_name, key=name_field)

    @execute_nosql
    def get_random_key(self):
        """ Выбираем случайный ключ.
        :return: Название случайного ключа
        """
        return {"type": "randomkey"}

    @staticmethod
    def form_key_redis(*items):
        """ Формируем полный путь-ключ для redis.
        :param keys: список ключей и путей, type=set
        :return:
        """
        return str(map(str, items)).replace("'", "").replace(', ', ':')[1:-1]

    def __init__(self, func):
        self.func = func


class ClassRedis():

    def __init__(self, host, port, name, user=None, passwd=None):
        # параметры аутетификации к БД
        self.auth = {"host": host, "port": port, "db": name, "user": user, "password": passwd}
        self.auth = funcy.compact(self.auth)
        service_log.put("Get params for authenticate with redis: %s" % self.auth)

        # параметры для работы внутри БД
        self.pool = None
        self.cursor = None
        self.cursor_now = None

    def connect(self):
        """ Устанавливает коннект с redis.
        Пример: redis.ConnectionPool(host='vm-fedor.home.oorraa.net', port=6379, db=0)
        :return: ссылка на коннект
        """
        self.pool = redis.ConnectionPool(**self.auth)
        service_log.put("Create connection pool: %s" % self.pool)
        r = redis.Redis(connection_pool=self.pool)
        service_log.put("Connect with redis is success: %s" % r)
        return r

    def execute(self, req, fetch='all'):
        """ Выполнить запрос.
        :param req: nosql-запрос
        :param fetch: тип выборки строк запроса
        :return: результат операции
        """
        try:
            self.cursor_now = self.connect()
            # Динамическое выполнение кода, параметр type - название функции в пуле коннекта
            if type(req) is dict:
                local_code = {"cursor_now": self.cursor_now}

                # Определяем количество параметров для передачи их функции
                if len(req) > 1:
                    name_funct = req.pop("type")
                    code_execution = """result = cursor_now.%s(**%s)""" % (name_funct, req)
                elif len(req) == 1:
                    code_execution = """result = cursor_now.%s()""" % (req.pop("type"))
                else:
                    msg = "Params for function is empty."
                    service_log.error(msg)
                    raise AssertionError(msg)

                service_log.put("Dynamic code execution: %s." % code_execution)
                exec code_execution in local_code
                service_log.put("Result dynamic code execution: %s." % local_code["result"])
                return local_code["result"]
            else:
                msg = "Not found type operation for redis."
                service_log.error(msg)
                raise AssertionError(msg)
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            self.close(self.cursor_now)

    def close(self, cursor):
        """ Закрываем соединение.
        :param cursor: ссылка на курсор
        """
        self.pool.disconnect()
        service_log.put("Closing opened redis connections.")