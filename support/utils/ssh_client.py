# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс для работы с SSH.
#--------------------------------------------------------------------

__author__ = 'Strubachev'
import paramiko
from dbase_methods.db_accounting import ClassAccountingSql
from dbase_methods.db_session import ClassSessionNoSql
from dbase_methods.db_messaging import ClassMessagingNoSql
from support import service_log, configs
from support.utils.db_postgresql import ClassPsyCopg2
from support.utils.db_redis import ClassRedis
from support.utils.variables import TVariables


def execute_ssh(func):
    """ Обертка для исполнения ssh-запросов.
    :type func: __builtin__.function
    :return: ссылка на функцию, с уже исполненым ssh-запросом
    """
    # TODO: Добавить более продуманное разделение на fechone, fetchall, commit
    def modify(*args, **kwargs):
        request = func(*args, **kwargs)
        ex = args[0].__dict__["func"]
        service_log.put("Shell command: %s" % request)
        result = ex(request)
        service_log.put("Shell command result: %s" % result)
        return result
    return modify


class ClassSaveLinkSSH():
    """
    Класс прородитель для хранения ссылки на функцию испольнения запросов.
    """
    def __init__(self, func):
        self.func = func


class ClassSSHClient():
    """
    Класс работы с SSH.
    """

    def __init__(self, host, port, user, passwd=None, keyfile=None):
        # параметры аутетификации к SSH
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd
        self.keyfile = keyfile

        self.client = None
        self.chanel = None

    def connect_by_user_password(self):
        """ Коннектимся к удалённой консоли.
        :return: возвращаем ссылку на терминал
        """
        try:
            client = paramiko.SSHClient()
            type_host_key = paramiko.AutoAddPolicy()
            client.set_missing_host_key_policy(type_host_key)  # add ssh-key in list keys — file .ssh/known_hosts
            client.connect(hostname=self.host, username=self.user, password=self.passwd, port=int(self.port))
            service_log.put("Open SSH connections.")
            return client
        except Exception, tx:
            msg_error = "SSH not connections! /n %s" % tx
            service_log.error(msg_error)
            raise msg_error

    def connect_by_key_file(self):
        """ Коннектимся к удалённой консоли по ключу.
        :return: возвращаем ссылку на терминал
        """
        try:
            client = paramiko.SSHClient()
            type_host_key = paramiko.AutoAddPolicy()
            client.set_missing_host_key_policy(type_host_key)  # add ssh-key in list keys — file .ssh/known_hosts
            client.connect(hostname=self.host, username=self.user, port=int(self.port), key_filename=self.keyfile)
            service_log.put("Open SSH connections.")
            return client
        except Exception, tx:
            msg_error = "SSH not connections! /n %s" % tx
            service_log.error(msg_error)
            raise msg_error

    def command_execution(self, cls, flag_output=True):
        """ Выполнить оперцию на удалённой консоли.
        :param client: ссылка на удалённую консоль
        :param cls: команда, которую необходимо запустить
        :param flag_output: если флаг False, то результат не возвращаем
        :return: Результат выполненной операции, либо ничего
        """
        if self.passwd is not None:
            client = self.connect_by_user_password()
        elif self.keyfile is not None:
            client = self.connect_by_key_file()
        else:
            msg_error = "Not found password or keyfile for connect!"
            service_log.error(msg_error)
            raise AssertionError(msg_error)
        try:
            service_log.put("Execute: %s." % cls)
            if flag_output is True:
                stdin, stdout, stderr = client.exec_command("""%s""" % cls)
                data = dict(stdout=stdout.read(), stderr=stderr.read())
                if data["stderr"] != '':
                    service_log.put("Return. Output: %s" % str(stderr))
                    service_log.put("Execute success. Output: %s" % str(data))
                    raise AssertionError("Return error: %s" % str(stderr))
                service_log.put("Execute success. Output: %s" % str(data))
                return data
            else:
                client.exec_command("""%s""" % cls)
                service_log.put("Execute success.")
                return None
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            self.close_connect(client)

    def sudo_command_execution(self, cls, passwd=None):
        """
        Make a remote command execution with sudo by ssh
        Return result
        :param cls: remote command to run
        """
        client = self.connect()
        channel = None
        try:
            service_log.put("Open SSH chanel.")
            channel = client.get_transport().open_session()
            service_log.put("Open SSH chanel success.")

            channel.get_pty()
            channel.settimeout(5)

            service_log.put("Execute: %s." % cls)
            #self.channel.exec_command('sudo -i')
            channel.exec_command('sudo %s' % cls)
            if passwd is not None:
                channel.send(self.passwd+'\n')
            data = channel.recv(1024)
            service_log.put("Execute success. Output: %s" % str(data))
            return data
        except Exception, tx:
            service_log.error(str(tx))
            raise AssertionError(str(tx))
        finally:
            self.close_connect(client, channel)

    def close_connect(self, client, channel=None):
        """
        Close connection SSH if exist
        """
        try:
            if self.channel:
                self.channel.close()
                self.channel = None

            if self.client:
                self.client.close()
                self.client = None

        except Exception, tx:
            service_log.error("SSH connection not success close.")
        service_log.put("SSH connection close.")


