# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс работы с Oralce.
#--------------------------------------------------------------------
from support import service_log
from support.databases.db_oracle import ClassSaveLinkOracleSQL, execute_sql, execute_procedure
from support.utils.common_utils import run_on_prod


__author__ = 'senchuk'


class ClassGetOracleSql(ClassSaveLinkOracleSQL):

    @execute_sql
    def get_data_by_account(self, param):
        """ Пример получения информацию из таблицы <name_table> по соответствию параметра param.
        :param param: параметр для поиска условия
        :return: данные таблицы <name_table>
        """
        # todo: слишком общий метод - делает код запутанным
        p = """SELECT * FROM tbg.crp_agreements WHERE accountid = %s""" % param
        service_log.put("Select user data: %s" % p)
        return p

    @execute_procedure
    def get_agreement_info(self, named_params, output):
        """
        Выполнить процедуру get_agreement_info
        :param named_params:
        :param out_param:
        :return:
        """
        script = """
        declare
            XML_IN XMLTYPE;
            XML_OUT XMLTYPE;
            ERROR_KEY1 number;
            ERROR_MES1 Varchar2(100);
            ERROR_DETAIL1 Varchar2(100);
            begin
                XML_IN := xmltype(:in_param);
                LT_DBO_REQUEST_API.GETAGREEMENTINFO(XML_IN, XML_OUT, ERROR_KEY1, ERROR_MES1, ERROR_DETAIL1);
                :out_param := XML_OUT.getStringVal();
                :err_msg := ERROR_MES1;
                :err_det := ERROR_DETAIL1;
            end;
        """
        return script


class ClassUpdateOracleSql(ClassSaveLinkOracleSQL):
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


class ClassOracleSql(ClassGetOracleSql, ClassUpdateOracleSql,):
    """ --== Класс буфер. ==--
    Содержит методы группирующие вызовы методов родительских классов.
    """
    pass






