# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Tests accounting worker.
#--------------------------------------------------------------------
import random
from unittest import skip, expectedFailure
from ddt import ddt, data
from support import service_log
from support.databases.db import databases
from support.utils.common_utils import run_on_prod
from tests.new_service.support_methods.class_new_service import NewApiCheckMethods


__author__ = 'senchuk'


@ddt
class TestNewAPI(NewApiCheckMethods):

    @classmethod
    def setUp(cls):
        """ Пре-установка окружения для теста.
        """
        service_log.preparing_env(cls)

    @data(1, 2, 3)
    def test_api1(self, val=1):
        """
        Пример описания теста.
        """
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