# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Tests accounting worker.
#--------------------------------------------------------------------
import os
from unittest import skip, expectedFailure
from ddt import ddt, data
from support import service_log
from support.databases.db import databases
from support.utils.common_utils import run_on_prod
from tests.new_service.support_methods.class_new_service import NewApiCheckMethods
import cx_Oracle


__author__ = 'senchuk'


@ddt
class TestNewAPI(NewApiCheckMethods):

    @classmethod
    def setUp(cls):
        """ Пре-установка окружения для теста.
        """
        NLS_LANG = 'RUSSIAN.CL8MSWIN1251'
        os.environ['NLS_LANG'] = NLS_LANG
        service_log.preparing_env(cls)

    def test_GetAgreementInfo(self):
        """
        Тест на метод GetAgreementInfo
        """
        in_param = '<GetAgreementInfoIn><AgreeId>10011948</AgreeId><Details>1</Details></GetAgreementInfoIn>'
        out_param = cx_Oracle.STRING
        err_msg = cx_Oracle.STRING
        err_det = cx_Oracle.STRING
        output = ['out_param', 'err_msg', 'err_det']
        named_params = {'in_param': in_param, 'out_param': out_param, 'err_msg': err_msg, 'err_det': err_det}
        proc_res = databases.db1.oracle.get_agreement_info(named_params, output)
        self.assertEqual(proc_res['err_msg'], None)
        self.assertEqual(proc_res['err_det'], None)
        self.assertNotEqual(proc_res['out_param'], None)
        out_xml = proc_res['out_param'].decode('cp1251').encode('utf-8')

        # Пример выполнения sql запроса
        #p = databases.db1.oracle.get_data_by_account(param='10011948')
        #print(out_xml)
        #print(p)
        pass

    @run_on_prod(False)
    def test_api2(self, val=1):
        """
        Пример описания теста.
        Warning: не запускается с конфигом on_prod
        """
        # Пример работы с БД
        # self.data = databases.db1.new_api.get_data_by_id(val)[0]
        pass

    @skip("todo")
    def test_api3(self):
        """
        Пример описания теста.
        """
        # todo: пример пропуска теста
        pass


    @classmethod
    def tearDown(cls):
        """ Пост-работа после завершения теста.
        """
        service_log.end()