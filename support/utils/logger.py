# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Логирование.
#--------------------------------------------------------------------
__author__ = 'Strubachev'

import logging
import logging.config
import sys
import os

class InitializationLogger():

    LOGGER_NAME = 'ftest'
    LOGGER_CONFIG = r"{0}{1}configs{1}logger.cfg"
    LOGGER_DATA = LOGGER_NAME + '.log'
    TMP = r"{0}tmp{0}"


    def __init__(self):
        opsys = sys.platform
        if 'win32' == opsys.lower() or 'win64' == opsys.lower():
            self.sep = '\\'
        else:
            self.sep = r'/'
        #self.logger_config = "C:\Freelance_hg\py-test\configs\logger.cfg"
        self.logger_config = InitializationLogger.LOGGER_CONFIG.format(os.getcwd(), self.sep)
        self.folder_log = InitializationLogger.TMP.format(self.sep)
        self.path = os.getcwd() + self.folder_log

        # Очищаем лог перед началом тестирования
        f = open(self.path + InitializationLogger.LOGGER_DATA, 'w')
        f.write("---== Start testing. ==---\n\r")
        f.close()

    def get_logger(self):
        #  Конфигурация логгирования
        logging.config.fileConfig(self.logger_config)
        return logging.getLogger(InitializationLogger.LOGGER_NAME)


class LoggerInfo():
    def __init__(self, log):
        self.main_log = log

    def put(self, text):
        """ Логирование общей информации.
        :param text: текст которые слудует положить в лог файл
        """
        self.main_log.info(text)

    def user(self, user):
        msg = "Get user, id=%s: %s" % (user["id"], user)
        self.main_log.info(msg)

    def error(self, text):
        """ Логирование ошибки.
        :param text: текст которые слудует положить в лог файл
        """
        self.main_log.info("Error: " + str(text))

    def warning(self, text):
        """ Логирование предупреждения.
        :param text: текст которые слудует положить в лог файл
        """
        self.main_log.info("Warning: " + text)

    def c_request(self, data):
        """ Логирование созданных запросов.
        :param data: Созданный для отправки сервису запрос
        """
        self.main_log.info("Create request json-rpc for service: %s" % data)

    def s_response(self, data):
        """ Логирование ответов.
        :param data: Созданный для отправки сервису запрос
        """
        self.main_log.info("Response json-rpc from service: %s" % data)

    def preparing_env(self, data):
        """ Логирование запуска теста.
        :param data: глобальные переменные
        """
        self.main_log.info("\n\n == Preparing the test environment ==")
        self.main_log.info("Link Test: %s " % str(data).replace("'", ''))

    def run(self, data):
        """ Логирование запуска теста.
        :param data: глобальные переменные
        """
        self.main_log.info("\n\n == Run Test ==")
        self.main_log.info("Name Test: %s " % data._testMethodName)

    def end(self):
        """ Логирование завершения теста.
        """
        self.main_log.info("\n *** The test TearDown ***")
