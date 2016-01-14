# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс для работы с БД Oracle.
#--------------------------------------------------------------------

from support import service_log
import cx_Oracle

__author__ = 'senchuk'


def rows_to_dict_list(cursor):
    """
    cx_Oracle cursor - return named tuple
    :param cursor:
    :return:
    """
    columns = [i[0] for i in cursor.description]
    return [dict(zip(columns, row)) for row in cursor]


def execute_sql(func):
    """ Обертка для исполнения sql-запросов.
    :type func: __builtin__.function
    :return: ссылка на функцию, с уже исполненым sql-запросом
    """
    # TODO: Добавить более продуманное разделение на fechone, fetchall, commit
    def modify(*args, **kwargs):
        request = func(*args, **kwargs)
        ex = args[0].__dict__["func"]
        service_log.put("SQL-query: %s" % request)
        if request[:6].upper() == "UPDATE":
            result = ex(request, "update")
        elif request[:6].upper() == "INSERT":
            result = ex(request, "insert")
        else:
            result = ex(request, "all")
        service_log.put("SQL-query result: %s" % result)
        return result
    return modify


def execute_procedure(func):
    """ Обертка для исполнения procedure sql-запросов.
    :type func: __builtin__.function
    :return: ссылка на функцию, с уже исполненым sql-запросом
    """
    def modify(*args, **kwargs):
        print args
        print kwargs
        request = func(*args, **kwargs)
        ex = args[0].__dict__["func"].im_self.execute2
        service_log.put("Procedure SQL-query: %s" % request)
        result = ex(request, args[1], args[2])
        service_log.put("Procedure SQL-query result: %s" % result)
        return result
    return modify


class ClassSaveLinkOracleSQL():
    """
    Класс прородитель для хранения ссылки на функцию испольнения запросов.
    """
    def __init__(self, func):
        self.func = func


class ClassCxOracle():
    """
    Класс работы с Oracle.
    """

    def __init__(self, host, port, name, user, passwd):
        # параметры аутетификации к БД
        self.host = host
        self.port = port
        self.name = name
        self.user = user
        self.passwd = passwd

        # параметры для работы внутри БД
        self.conn = None
        self.cursor = None
        self.cursor_now = None

    def connect(self):
        """ Коннектимся с базой.
        :param cursor_view: вид в котором возвращается ответ (по умолчанию - dict, словарь)
        :return: возвращаем курсор
        """
        connection_str = '%s/%s@%s:%s/%s' % (self.user, self.passwd, self.host, self.port, self.name)
        self.conn = cx_Oracle.connect(connection_str)
        cursor = self.conn.cursor()
        service_log.put("Open oracle connections.")
        return cursor

    def execute2(self, req, named_params, output):
        """ Выполнить запрос.
        :param req: sql-запрос
        :param fetch: тип выборки строк запроса
        :return: результат операции
        """

        try:
            self.cursor_now = self.connect()
            for param in named_params:
                if isinstance(named_params[param], type):
                    named_params.update({param: self.cursor_now.var(named_params[param])})
            self.cursor_now.execute(req, named_params)
            output = {out: named_params[out].getvalue() for out in output}
            service_log.put("Commit operation UPDATE.")
            return output
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            self.close(self.cursor_now)

    def execute(self, req, fetch='all'):
        """ Выполнить запрос.
        :param req: sql-запрос
        :param fetch: тип выборки строк запроса
        :return: результат операции
        """
        try:
            self.cursor_now = self.connect()
            self.cursor_now.execute(req)
            if fetch == "all":
                result = rows_to_dict_list(self.cursor_now)
                service_log.put("Fetchall rows.")
                return result
            elif fetch == "one":
                result = self.cursor_now.fetchone()
                service_log.put("Fetchone rows.")
                return result
            elif fetch == "update" or fetch == "insert":
                service_log.put("No fetch rows. Operation by UPDATE.")
                self.conn.commit()
                service_log.put("Commit operation UPDATE.")
                return None
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            self.close(self.cursor_now)



    def close(self, cursor):
        """ Закрываем соединение.
        :param cursor: ссылка на курсор
        """
        #cursor.close()
        #self.conn.close()
        service_log.put("Closing opened oracle connections.")