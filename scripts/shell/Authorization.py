# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Работы через SSH.
#--------------------------------------------------------------------

from support.utils.ssh_client import ClassSaveLinkSSH, execute_ssh

__author__ = 'Strubachev'


class ClassAuthorization(ClassSaveLinkSSH):

    @execute_ssh
    def command_curl(self, request, url_serv, accept_encoding_flag=True):
        """ Отправляем запросы через curl.
        :param request: запрос
        :param url_serv: url-сервера
        :param accept_encoding_flag: флаг
        """
        content_type = "Content-type: application/json-rpc"
        accept_encoding = "Accept-Encoding: gzip,deflate,sdch"

        curl = lambda a, b, c, d: """curl "%s" -H "%s" -H "%s" --data-binary '%s' --compressed """ % (a, b, c, d)
        curl_without_accept = lambda a, b, c: """curl "%s" -H "%s" --data-binary '%s' --compressed """ % (a, b, c)

        if accept_encoding_flag is True:
            cls = curl(url_serv, accept_encoding, content_type, request)
            return cls
        else:
            cls = curl_without_accept(url_serv, content_type, request)
            return cls

    @execute_ssh
    def command_ps_for_java_process(self, name="jar", profile="holland"):
        """ Get list current processes.
        :param path: search keyword
        :return: list with current processes
        """
        return " ps aux | grep %s" % name

    @execute_ssh
    def command_ls(self, path="."):
        """ Get list directory contents.
        :param path: path directory
        :return: list with names all files and folders in directory
        """
        return "ls %s" % path

    @execute_ssh
    def command_who(self):
        """ Вернуть пользователя под которым работаем с удалённой консолью.
        Тестовый метод.
        """
        return "who"

    @execute_ssh
    def get_logs(self, phone):
        """ Получить логи вывода от сервиса.
        :param phone: номер телефона
        :return: info-потоков
        """
        #txt = "'%s, txt:Ваш новый пароль доступа к сервису http://oorraa.com'" % phone
        #cmd = "grep -n %s /var/log/oorraa/accounting-worker/accounting-worker.log | tail -1" % txt
        txt = "%s, txt:" % phone
        cmd = "grep -n '%s' /var/log/oorraa/accounting-worker/accounting-worker.log | tail -1" % txt
        return cmd

    @execute_ssh
    def set_metric(self, input_str, cur_time):
        """ Получить логи вывода от сервиса.
        :param phone: номер телефона
        :return: info-потоков
        """
        cmd = 'echo local.load_average %s %s | nc 10.2.40.152 2003' % (input_str, cur_time)
        return cmd

    @execute_ssh
    def get_logs_sms(self, phone):
        """ Получить логи вывода от сервиса.
        :param phone: номер телефона
        :return: info-потоков
        """
        #txt = "'%s, txt:Ваш новый пароль доступа к сервису http://oorraa.com'" % phone
        #cmd = "grep -n %s /var/log/oorraa/accounting-worker/accounting-worker.log | tail -1" % txt
        txt = "%s, txt:" % phone
        cmd = "grep -n '%s' /var/log/oorraa/sms-worker/sms-worker.log | tail -1" % txt
        return cmd




