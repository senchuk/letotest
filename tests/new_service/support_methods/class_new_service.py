# -*- coding: utf-8 -*-
# --------------------------------------------------------------------
#         	Пример файла с классами для работы с заданной функциональностью.
# --------------------------------------------------------------------
#from __future__ import unicode_literals
import base64
import hashlib
import json
import random
import time
from support import service_log
from support.class_main import MainClass
from tests.new_service.dbase_methods.db_new_service import ClassGetNewApiSql
import requests
import datetime

__author__ = 'senchuk'


class NewApiData(MainClass):
    """
    Статические данные: переменные, константы, названия классов и т.д.
    """


class NewAPIMethods(NewApiData):
    @staticmethod
    def get_data(param):
        """ Пример статического метода.
        :param param: параметр
        :return: <param>
        """
        return param


class NewApiCheckMethods(NewAPIMethods):
    pass
