# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Работа с Jenkins ч/з ssh.
#       url-info: http://selenium.oorraa.pro:8080/cli/
#--------------------------------------------------------------------

__author__ = 's.trubachev'


class JenkinsCmd():

    def __init__(self):
        """ Определяем синтаксис командной строки для работы с Jenkins.
        Работает в связке с ssh.
        """
        host = "http://selenium.oorraa.pro:8080/"
        jar_path = ""
        jar_file = "jenkins-cli.jar"
        jar_cmd = jar_path + jar_file
        self.main_cmd = "java -jar %s -s %s " % (jar_cmd, host)

    def restart(self):
        """ Перезагрузка Jenkins.
        Например: java -jar jenkins-cli.jar -s http://selenium.oorraa.pro:8080/ restart
        :return: строка с командой
        """
        return self.main_cmd + "restart"

    def login(self):
        """ Сохраняет текущие учетные данные, позволяет в будущем
        запускать команды без явного указания учетных данных.
        :return: строка с командой
        """
        return self.main_cmd + "login"

    def shutdown(self):
        """ Погасить Jenkins.
        Завершение работы Jenkins.
        :return: строка с командой
        """
        return self.main_cmd + "shutdown"

    def version(self):
        """ Вывод текущей версии.
        :return: строка с командой
        """
        return self.main_cmd + "version"
