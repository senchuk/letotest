# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс для работы с БД PostreSQL.
#--------------------------------------------------------------------

from support import service_log
import psycopg2
import psycopg2.extras

__author__ = 'Strubachev'


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


class ClassSaveLinkPostgreSQL():
    """
    Класс прородитель для хранения ссылки на функцию испольнения запросов.
    """
    def __init__(self, func):
        self.func = func


class ClassPsyCopg2():
    """
    Класс работы с PostgreSQL.
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

    def connect(self, cursor_view="dict"):
        """ Коннектимся с базой.
        :param cursor_view: вид в котором возвращается ответ (по умолчанию - dict, словарь)
        :return: возвращаем курсор
        """
        cursor_factory = psycopg2.extras.DictCursor if cursor_view == "dict" else psycopg2.extras.NamedTupleCursor
        self.conn = psycopg2.connect(host=self.host, port=self.port, dbname=self.name, user=self.user,
                                     password=self.passwd, cursor_factory=cursor_factory)
        cursor = self.conn.cursor()
        service_log.put("Open postgresql connections.")
        return cursor

    def execute(self, req, fetch='all', cursor_view="dict"):
        """ Выполнить запрос.
        :param req: sql-запрос
        :param fetch: тип выборки строк запроса
        :return: результат операции
        """
        what_cursor_view = lambda view, element: dict(element) if view == "dict" else element
        try:
            self.cursor_now = self.connect(cursor_view=cursor_view)
            self.cursor_now.execute(req)
            if fetch == "all":
                result = self.cursor_now.fetchall()
                service_log.put("Fetchall rows.")
                return [what_cursor_view(cursor_view, elem) for elem in result]
            elif fetch == "one":
                result = self.cursor_now.fetchone()
                service_log.put("Fetchone rows.")
                return what_cursor_view(cursor_view, result)
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
        service_log.put("Closing opened postgresql connections.")