# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс для работы с SSH.
#--------------------------------------------------------------------
__author__ = 'Strubachev'

from shell_scripts.Authorization import ClassAuthorization
from support.utils.ssh_client import ClassSSHClient
from support import service_log, configs
from support.utils.variables import TVariables


class ClassShellWork():

    prefix_shell = ["ssh"]

    def __init__(self, shell_host=None, shell_port=None, shell_type=None, shell_user=None, shell_passwd=None,
                 shell_keyfile=None):
        self.params_authentication = {"host": shell_host,
                                      "port": shell_port,
                                      "user": shell_user,
                                      "passwd": shell_passwd,
                                      "keyfile": shell_keyfile}
        self.shell_type = shell_type

    def __getattr__(self, item):
        if item in self.find_prefixes_shell():
            #global prefix_ssh
            values_authentication = dict()
            try:
                values_authentication = {
                    "shell_host": configs.config["env_info"][item + "_host"],
                    "shell_port": configs.config["env_info"][item + "_port"],
                    "shell_user": configs.config["env_info"][item + "_user"],
                    "shell_type": item[:3],  # TODO: при добавалении новых типов shell изменить
                }

                if item + "_passwd" in configs.config["env_info"]:
                    # есть пароль, используем пароль
                    # "shell_passwd": configs.config["env_info"][item + "_passwd"],
                    values_authentication.update({"shell_passwd": configs.config["env_info"][item + "_passwd"]})
                elif item + "_keyfile" in configs.config["env_info"]:
                    # используем ключ, указываем путь до ключа
                    values_authentication.update({"shell_keyfile": configs.config["env_info"][item + "_keyfile"]})
                else:
                    raise AssertionError("Not found password or keyfile for shell.")

            except Exception, tx:
                service_log.error("Not found mark in env.cfg: %s" % str(tx))
            return ClassShellWork(**values_authentication)
        elif item in TVariables.thrift.workers:

            # карта сервисов и типов соответствия их с ssh
            sv = {"ssh": {"authorization": [ClassAuthorization, ClassSSHClient]},
                  }

            for name_type, service_value in sv.iteritems():
                if name_type == 'ssh':
                    for name_service, links_service in service_value.iteritems():
                        if item == name_service:
                            return links_service[0](links_service[1](**self.params_authentication).command_execution)
                    else:
                        msg_error = "Not found class for the work with shell."
                        service_log.error(msg_error)
                        raise AssertionError(msg_error)
            else:
                msg_error = "Not detected type shell in env.cfg!"
                service_log.error(msg_error)
                raise AssertionError(msg_error)

    @staticmethod
    def find_prefixes_shell():
        bases_val = [key for key in configs.config["env_info"].keys() if key[:3] in ClassShellWork.prefix_shell]
        prefixes = set([index[:index.find("_")] for index in bases_val])
        if len(prefixes) != 0:
            return prefixes
        else:
            msg_error = "Not found prefix for connect with shell!"
            service_log.error(msg_error)
            raise AssertionError(msg_error)


shell = ClassShellWork()