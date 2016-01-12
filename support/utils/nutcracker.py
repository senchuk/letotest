# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------
#         	Классы и методы для работы с БД no-sql Redis через Nutcracker.
#
#------------------------------------------------------------------------------------
import funcy
from support import service_log, configs

__author__ = 's.trubachev'


class ClassNutcracker():

    def __init__(self, name_exc_item, conns=None):
        """ Инициализируем объект ClassNutcracker
        :param name_exc_item: название объекта, который вызвал этот класс
        :param conns: список соеденений через список др.объектов
        """
        self.name_exc_item = name_exc_item
        self.conns = conns

    def __getattr__(self, item):
        """ Определяем порядок вызова атрибутов.
        :param item: название атрибута
        :return: объект ClassNutcracker
        """
        if item == "shards":
            return ClassNutcracker(self.name_exc_item)
        elif item == "only":
            # для соеденения через прокси
            self.connections_proxy()
        elif item is not None and self.conns is None:
            conns = self.connections_to_db(self.__get_shards_data__(self.name_exc_item)["dbshards"])
            result = self.__iterable_exec(item, conns)
            return ClassNutcracker(item, result)
        else:
            return ClassNutcracker(item, self.conns)

    def __call__(self, *args, **kwargs):
        """ Подменяем вызов функции на её динамическое использование.
        :param args: аргументы передаваемые функции
        :param kwargs: аргументы передаваемые функции
        :return:
        """
        call_m = self.__iterable_exec(self.name_exc_item, self.conns)
        result = [index(*args, **kwargs) for index in call_m]
        result_c = funcy.compact(result)
        if len(result_c) >= 2:
            msg_error = "Found several response!"
            service_log.error(msg_error)
            raise AssertionError(msg_error)
        else:
            service_log.put("Get response from nutcracker.")
            if len(result_c) == 0:
                return result_c
            else:
                return result_c[0]

    @staticmethod
    def __iterable_exec(item, conns):
        """ Динамически подгружаем ссылке на связанные с БД классы.
        :param item: название объекта
        :param conns: соеденения
        :return: список с результатом работы
        """
        result = list()
        for conn in conns:
            local_code = None
            exec """local_code = conn.%s""" % item in local_code
            if local_code is not None:
                result.append(local_code)
            else:
                msg_error = "Not found attribute '%s' " % item
                service_log.error(msg_error)
                raise AssertionError(msg_error)
        return result

    def connections_to_db(self, shards):
        """ Соеденения со всеми шардами по отдельности.
        :param shards: список названий шардов
        :return: список соеденений ClassDatabasesWork
        """
        from support.utils.db import ClassDatabasesWork
        return [ClassDatabasesWork(**self.__get_shard_data__(shard.strip()))for shard in shards]

    @staticmethod
    def __get_shard_data__(shard):
        """ Собрать информацию для конкретного шарда.
        :param shard: имя префикса шарда с данными для атворизации
        :return: данные коннекшена
        """
        values_authentication = {"dbhost": configs.config["env_info"][shard + "_host"],
                                 "dbtype": configs.config["env_info"][shard + "_type"],
                                 "dbname": configs.config["env_info"][shard + "_name"]}
        # Могут быть необязательные поля
        if shard + "_port" in configs.config["env_info"].keys():
            values_authentication.update({"dbport": configs.config["env_info"][shard + "_port"]})
        if shard + "_passwd" in configs.config["env_info"].keys():
            values_authentication.update({"dbpasswd": configs.config["env_info"][shard + "_passwd"]})
        if shard + "_login" in configs.config["env_info"]:
            values_authentication.update({"dbuser": configs.config["env_info"][shard + "_login"]})
        return values_authentication

    @staticmethod
    def __get_shards_data__(item):
        """ Для шардирования, запоминаем конфигурационные данные.
        :param item: имя nutcracker
        :return: данные коннекшена
        """
        values_authentication = {"dbhost": configs.config["env_info"][item + "_host"],
                                 "dbtype": configs.config["env_info"][item + "_type"],
                                 "dbport": configs.config["env_info"][item + "_port"],
                                 "dbshards": configs.config["env_info"][item + "_shards"][1:-1].split(",")}
        return values_authentication

    def connections_proxy(self):
        # TODO: прямое подключение к proxy
        pass