# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#              Классы для работы с заданными конфигурацией переменными.
# PS: Отладка изначально вдвое сложнее написания кода.
#     Поэтому, если вы пишете код настолько заумный, насколько можете, то по определению вы не способны отлаживать его.
#       (c)Брайан Керниган и П.Ж.Плауэр, «Основы программного стиля»
#--------------------------------------------------------------------
import json
import funcy
from support import *
from support import service_log, configs


__author__ = 'Strubachev'


class GetVariableDataBase():
    # TODO: --//--
    pass


class GetVariableSSH():
    # TODO: --//--
    pass


class GetVariableRabbitMQ():
    """
    Класс для работы с заданными переменными для RabbitMQ.
    """

    # Переменные, которые должны быть определены для корректной работы с RabbitMQ
    __rabbit_variable_env = ["rabbit_login", "rabbit_passwd", "rabbit_host", "rabbit_port"]

    def __init__(self, conf):
        """ Инициализируем класс для работы с переменными RabbitMQ
        :param conf: ссылка на конфигурацию
        """
        self.env_conf = conf["env_info"]

    def __getattr__(self, item):
        """ Делаем проверку на существование переменных для работы RabbitMQ.
        :param item: наименование переменной, значение которой следует вернуть
        """
        # TODO: определить что в mail.cfg есть не пустые модули
        for num, var in enumerate(self.__rabbit_variable_env):
            if var not in self.env_conf:
                msg_not_found = "Not found variable '%s' in env.cfg" % var
                service_log.error(msg_not_found)
                raise AssertionError(msg_not_found)

            if self.env_conf[var] == "":
                msg_empty = "Variable '%s' in env.cfg is empty" % var
                service_log.error(msg_empty)
                raise AssertionError(msg_empty)

            if var == "rabbit_" + item:
                return self.env_conf[self.__rabbit_variable_env[num]]
        else:
            msg_not_defined = "Variable is not defined correctly."
            service_log.error(msg_not_defined)
            raise AssertionError(msg_not_defined)


class GetVariableService():
    """
    Класс для работы с заданными переменными для различных сервисов.
    """

    # Взять переменные сервисов из env.cfg
    # Пример: 'version_ds=1.1.0-SNAPSHOT' вызывается 'service_variable.ds.version'
    # Warning: работает только для сервисов (переменные БД, SSH и пр. не передаются)

    def __init__(self, cfg):
        """ Инициализация переменных различных сервисов.
        :param cfg: ссылка на конфигурацию
        """

        self.cfg = cfg

        try:
            # Ключевые слова, которые не являются префиксами
            #__kwords = ("host", "port", "name", "login", "passwd")
            __kwords = ()

            env_info = self.cfg["env_info"].keys()

            # определяем дополнительные функции для выборки префиксов сервисов
            num_pref = lambda a: a.rfind("_") if a.rfind("_") != -1 else False
            get_pref = lambda p: p[num_pref(p)+1:]
            get_name = lambda n: n[:num_pref(n)]
            no_kwords = lambda w, f: f(w) not in __kwords

            # Находим все префиксы сервисов
            self.array_var = set(get_pref(word) for word in env_info if num_pref(word) and no_kwords(word, get_pref))
            self.array_prefix = set(get_name(word) for word in env_info if num_pref(word) and no_kwords(word, get_name))
        except:
            msg_any_pref = "Unknown any prefix in env.cfg"
            service_log.error(msg_any_pref)
            raise AssertionError(msg_any_pref)

    def __getattr__(self, item):
        """ Делаем привязку к сервису.
        :param item: наименование префикса
        :return: возвращаем значение переменной из env_info.cfg или вызываем Exception
        """
        if item in self.array_prefix:
            global prefix_serv
            prefix_serv = item
            return GetVariableService(self.cfg)
        elif item in self.array_var:
            # возвращаем значение переменной из env_info.cfg
            return self.cfg["env_info"][prefix_serv+"_"+item]
        elif item in "is_prod":
            # если это конфиг для прода, возвращаем True, иначе False
            return self.cfg["env"].endswith("_on_prod")
        elif item in "what_env":
            # возвращаем название схемы окружения
            return self.cfg["env"]
        else:
            msg_pref = "Unknown prefix=%s in env.cfg" % item
            service_log.error(msg_pref)
            raise AssertionError(msg_pref)


class GetVariableThrift():
    # Взять переменные для работы с Thrift из env.cfg и main.cfg
    # Пример1, получить путь для импорта воркера: вызывается 'service.accounting.worker'
    # Пример2, url-воркера: вызывается 'service.accounting.url'
    # Пример3, переменную с версией thrift из main.cfg: вызывается 'service.thrift.version'
    # Пример4, или accounting_glob_path с путем ддо сгенерированных файлов: вызывается 'service.accounting.glob_path'
    # Warning: все определённые переменные должны содержать какой-то префикс!

    main_prefix = "thrift"

    def __init__(self, cfg):
        """ Инициализация переменных для сервиса thrift.
        :param cfg: ссылка на конфигурацию
        """

        self.cfg = cfg

        try:
            # Ключевые слова, которые не являются префиксами
            p_kwords = self.cfg["prefix"]["prefix_kwords"]
            p_import = "thrift_import_workers"

            # Находим все префиксы сервисов (см. раздел prefix main.cfg)
            array_user_prefix = self.cfg["prefix"]["prefix_local"][1:-1].split(',')
            prefix_sys = self.cfg["prefix"]["prefix_sys"][1:-1].split(',')
            array_all_prefix = array_user_prefix[:]
            array_all_prefix.append(GetVariableThrift.main_prefix)

            env_keys = self.cfg["env_info"].keys()
            thrift_data = self.cfg["thrift_variables"]
            thrift_keys = thrift_data.keys()

            # определяем дополнительные функции для выборки префиксов сервисов
            listmerge = lambda ll: [el for lst in ll for el in lst]
            del_word = lambda p, k: k.replace(p, '').strip('_')
            get_prefix = lambda: (index for index in array_all_prefix)
            find_prefix = lambda i, p: i.find(p) != -1


            # Получаем переменные из раздела thrift_variables в main.cfg
            if p_import in thrift_keys:
                # пути импорта файлов thrift
                self.dict_thrift_var = json.loads(thrift_data[p_import])


                # получаем список список переменных для поля thrift_import_workers
                temp_lists1 = lambda v: [del_word(pref, v) for pref in array_user_prefix if find_prefix(v, pref)]
                temp_lists2 = [temp_lists1(v) for v in self.dict_thrift_var.keys()]
                self.array_thrift_var1 = listmerge(temp_lists2)

                # получаем список список переменных для остального раздела thrift_variables
                temp_lists3 = lambda k: [del_word(p, k) for p in get_prefix() if k != p_import and find_prefix(k, p)]
                temp_lists4 = [temp_lists3(k) for k in thrift_keys]
                self.array_thrift_var2 = listmerge(temp_lists4)

                self.array_thrift_var = self.array_thrift_var1 + self.array_thrift_var2
                self.array_user_prefix = map(lambda a: a.split()[0], map(str, array_user_prefix))
                self.array_all_prefix = array_all_prefix
                self.prefix_sys = prefix_sys


        except:
            msg_any_pref = "Unknown any prefix in main.cfg or env.cfg"
            service_log.error(msg_any_pref)
            raise AssertionError(msg_any_pref)

    def __getattr__(self, item):
        """ Делаем привязку к сервису.
        :param item: наименование префикса
        :return: возвращаем значение переменной из env_info.cfg или вызываем Exception
        """
        if item in self.array_all_prefix:
            global prefix_serv
            prefix_serv = item
            return GetVariableThrift(self.cfg)
        elif item in self.array_thrift_var:
            if item in self.array_thrift_var1:
                # проверка, что нужна переменная импорта
                return self.dict_thrift_var[prefix_serv + "_" + item]
            elif item in self.array_thrift_var2:
                # проверка, что нужна одна из переменных в thrift_variables
                return self.cfg["thrift_variables"][prefix_serv + "_" + item]
        elif item == "imports" and prefix_serv in self.array_user_prefix:
            # только импорты определённого воркера
            res = dict([name, path] for name, path in self.dict_thrift_var.iteritems() if name.find(prefix_serv) != -1)
            return res
        elif item == "workers" and prefix_serv is GetVariableThrift.main_prefix:
            # список названий воркеров
            return self.array_user_prefix
        elif item == "imports" and prefix_serv is GetVariableThrift.main_prefix:
            # список всех импортов для Thrift
            return self.dict_thrift_var
        else:
            msg_pref = "Unknown prefix=%s in env.cfg" % item
            service_log.error(msg_pref)
            raise AssertionError(msg_pref)


TVariables = GetVariableThrift(configs.config)
EVariable = GetVariableService(configs.config)