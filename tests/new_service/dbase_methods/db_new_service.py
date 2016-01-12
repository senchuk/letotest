# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс работы с PostgreSQL.
#--------------------------------------------------------------------
from support import service_log
from support.databases.db_postgresql import ClassSaveLinkPostgreSQL, execute_sql
from support.utils.common_utils import run_on_prod


__author__ = 'senchuk'


class ClassGetNewApiSql(ClassSaveLinkPostgreSQL):

    @execute_sql
    def get_data_by_id(self, param):
        """ Пример получения информацию из таблицы <name_table> по соответствию параметра param.
        :param param: параметр для поиска условия
        :return: данные таблицы <name_table>
        """
        # todo: слишком общий метод - делает код запутанным
        p = """SELECT * FROM <name_table> WHERE <param> = %i;""" % param
        service_log.put("Select user data: %s" % p)
        return p


class ClassUpdateNewApiSql(ClassSaveLinkPostgreSQL):
    @execute_sql
    @run_on_prod(False)
    def update_data_by_id(self, param1, param2):
        """ Изменить соль пользователя.
        :param param1: <param1>
        :param param2: <param2>
        :return: None
        """
        # todo: слишком общий метод - делает код запутанным
        p = "UPDATE <name_table> SET <param1>='%s' WHERE <param2>='%s';" % (param1, param2)
        service_log.put("Update user data: %s" % p)
        return p


class ClassNewApiSql(ClassGetNewApiSql, ClassUpdateNewApiSql,):
    """ --== Класс буфер. ==--
    Содержит методы группирующие вызовы методов родительских классов.
    """
    pass






