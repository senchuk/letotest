# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Вспомогательные методы.
#        P.S: «Keep it simple, stupid!»
#--------------------------------------------------------------------
from collections import defaultdict
import hashlib
import json
import itertools
import requests

__author__ = 'Strubachev'

import random
import string
import cProfile
import urllib
import time
#from support.shell_scripts import * # TODO: нет библиотек
from support import service_log, configs
from regd import DecoratorRegistry as dreg


def random_string(params="all", length=10):
    """ Generate string of the desired length.
    Get length string.
    :return: Returns a string of letters and numbers.
    """
    if params == "all":
        return ''.join(random.choice(string.letters + string.digits) for x in range(length))
    elif params == "letters":
        return ''.join(random.choice(string.letters) for x in range(length))
    elif params == "digits":
        return ''.join(random.choice(string.digits) for x in range(length))
    elif params == "russian":
        string_russian = u"йцукенгшщзхъфывапролджэячсмитьбю"
        return ''.join(random.choice(string_russian) for x in range(length))


def unique_number(strategy=0):
    """ Получить уникальный номер.
    :return: уникальный номер
    """
    if strategy == 0:
        return int(time.time()) + random.randint(0, 10000000)

 # TODO: нет библиотек
#def query_by_new_bd():
#    """ Connect with an additional base, BD2 in env.config.
#    :return: return connection
#    """
#    bd2 = DB("db2_name")
#    bd2.connect(configs["env_info"]["db2_host"], configs["env_info"]["db2_login"], configs["env_info"]["db2_passwd"])
#    return bd2
#
#
#def connect_bd(function_to_decorate):
#    """ Additional base and execute the decorated function with the new settings.
#
#    When referring to the argument of 'db2_name' parameter 'connect', install new
#    database connection and execute the decorated function with the new settings.
#    If argument of 'db1_name' parameter 'connect', connect at source bd.
#    :param function_to_decorate: Source function
#    :return: decorated function with parameter 'connect'
#    """
#    def wrapper(**arg):
#        class BD2:
#            def __init__(self):
#                pass
#
#            def __getattr__(self, item):
#                if item == "db2_name":
#                    try:
#                        arg['accessible_db'] = query_by_new_bd()
#                        return function_to_decorate(**arg)
#                    except KeyError:
#                        return "There is no index name 'accessible_db' in the dictionary"
#                elif item == "db1_name":
#                    return function_to_decorate(**arg)
#        function_to_decorate.__setattr__("connect", BD2())
#        return function_to_decorate
#    return wrapper


def check_version_branch(decor_arg=None):
    """ Checking version branch before running test.
    If version testing branch not equals version branch in config do nothing.
    Else run test.
    :param decor_arg: list with version branch for testing or None
    :return: decorated method or empty method
    """
    # TODO: Добавить возможность указывать не конкретный бранч, а больше или меньше заданной версии.

    version_branch = configs.config["system_settings"]["version_branch"]

    def skip_method(method_to_decorate):
        """ To work correctly, you call the method
        with parameter of the decorated method.
        :param method_to_decorate: method_to_decorate
        :return: the empty function for pass test
        """
        def pass_funct(**args):
            pass
        return pass_funct

    if decor_arg is not None:
        for index in set(decor_arg):
            if version_branch == str(index) or version_branch == "anything":
                return dreg.get_real_function
        else:
            return skip_method
    else:
        return dreg.get_real_function


def run_on_prod(decor_arg):
    """ Запуск автотестов или запрет на это, в зависимости от того, на каком окружении они должны исполняться.
    Если decor_arg=True или это не продакшен, возвращаем ссылку на тест-кейз для дальнейшей его работы,
    если decor_arg=False возвращаем на "пустой" метод и тест-кейз не выполняется.
    Если decor_arg не является булевским типом - вызываем exception.
    :param decor_arg: True или False
    :return: ссылка на метод
    """
    if type(decor_arg) is not bool:
        raise TypeError("Type arguments decorator must be a Boolean.")
    environment = configs.config["env"]

    def skip_method(method_to_decorate):
        def pass_funct(*kwargs, **args):
            pass
        return pass_funct

    if (environment.endswith("_on_prod") is not True) or (decor_arg is True):
        return dreg.get_real_function
    else:
        return skip_method


def priority(decor_arg):
    """ Запуск автотестов или запрет на это, в зависимости от того, с каким приоритетом они должны исполняться.
    Если decor_arg=must или это не продакшен, возвращаем ссылку на тест-кейз для дальнейшей его работы,
    если decor_arg=high возвращаем ссылку на тест-кейз для дальнейшей его работы,
    если decor_arg=medium возвращаем ссылку на тест-кейз для дальнейшей его работы,
    если decor_arg=low возвращаем ссылку на тест-кейз для дальнейшей его работы,
    если decor_arg=don't возвращаем ссылку на тест-кейз для дальнейшей его работы,
    Если decor_arg не является стороковым типом - вызываем exception.
    :param decor_arg: True или False
    :return: ссылка на метод
    """
    map_pr = {
        'must': 1,
        'high': 2,
        'medium': 3,
        'low': 4,
        "don't": 5,
    }
    if type(decor_arg) is not str:
        raise TypeError("Type arguments decorator must be a String.")
    pr = str(configs.config["priority"]).lower()

    def skip_method(method_to_decorate):
        def pass_funct(*kwargs, **args):
            pass
        return pass_funct
    decor_arg = decor_arg.lower()
    if pr == 'none':
        return dreg.get_real_function
    elif map_pr[pr] == map_pr[decor_arg]:
        return dreg.get_real_function
    else:
        return skip_method


def intersection_lists(array):
    """ Делаем пересечение списка нескольких списков.
    :param array: список списков
    :return: Либо None, либо множество пересечений
    """
    if len(array) > 1 and type(array) == list:
        convert_to_set = lambda i: "set(%s)" % i
        inner = None
        exec("inner=" + " & ".join(map(convert_to_set, array)))
        return inner
    else:
        return None


def sub(first, second):
    """ Исключение элементов из списка.
    если a = [5,6,7] и b = [4,3,7]
    то a - b = [5, 6]
    :param first: первый список
    :param second: второй список
    :return: список элементов, которые не содержатся во втором списке
    """
    if type(first) and type(second) is list:
        return [a for a in first+second if (a not in first) or (a not in second)]


def save_file(url):
    """ Сохранить файл по url-ссылке.
    :param url: url файла
    :return: путь до локального расположения файла
    """
    webFile = urllib.urlopen(url)
    data = webFile.read()
    localFile = open(url.split('/')[-1], 'wb')
    localFile.write(webFile.read())
    webFile.close()
    localFile.close()
    return localFile


def generation_items_pairwise(combination, number_combinations=2):
    """ Функция формирования сочетаний полей для методов.
    Делаем сочетание элементов между собой, методика pairwise.
    :params combination: type(list) - список который со значениями
    :params number_combinations: type(int) - число одновременных сочетаний
    :return: type(list) - список сочетаний
    """

    combo_it = itertools.combinations(combination, number_combinations)
    combo_l = list(combo_it)
    random.shuffle(combo_l)
    variation = [[i[j] for j in range(number_combinations)] for i in combo_l]
    return variation


def generate_sha256(source_str, salt=None):
    """ Генератор строки в хеш SHA-256
    :param source_str: исходная строка
    :return: хеш
    """
    hhh = hashlib.sha256()

    # работа с паролем у которого есть соль
    if salt is None or salt == '':
        hhh.update(source_str)
    else:
        hhh.update(source_str + "{" + salt + "}")

    new_hash = hhh.hexdigest()
    service_log.put("Generate for new password (%s) its hash (%s)." % (source_str, new_hash))
    return new_hash


def hashSha256(str_h):
    hsh = hashlib.sha256()
    hsh.update(str_h)
    string=str(hsh.hexdigest())
    return string


def dict_to_json(params, ensure_ascii=True):
    """ Конвертировать словарь в json.
    :param params: словарь с данными
    :param ensure_ascii: если False, все не ASCII символы не будут выброшены.
    :return: json-строка
    """
    return json.dumps(params, ensure_ascii=ensure_ascii)


def json_to_dict(json_str):
    """ Конвертировать json в dict
    :param json_str: json-строка
    :return: dict
    """
    return json.loads(json_str)


def convert_dict_to_json(func):
    """ Вспомогательный декоратор, конвертирует вывод dict в str.
    WARNING: работает в связке с методом dict_to_json
    :type func: функция, которая возвращает словарь для конвертирования
    :return: строка с данными
    """
    def modify(*args, **kwargs):
        answer_func = func(*args, **kwargs)
        result = dict_to_json(answer_func)
        return result
    return modify


def url_decode(val):
    """ Декодировать url.
    :param val: строка
    :return: расшифрованые строки
    """
    import urllib
    return urllib.unquote_plus(val)


def instance_to_dict(instance_obj):
    """ Конвертировать объект в словарь,
    где ключи словаря соответсвуют названию объектов.
    :param instance_obj: очередной элемент
    :return: словарь с параметрами.
    """

    if str(type(instance_obj)) == "<type 'instance'>":
        # если это объект, конвертируем его в dict
        main_dict = dict()
        for index in instance_obj.__dict__:
            main_dict.update({index: instance_to_dict(instance_obj.__dict__[index])})
        return main_dict
    elif isinstance(instance_obj, list):
        # если это список
        return [instance_to_dict(index) for index in instance_obj]
    elif isinstance(instance_obj, tuple):
        # если это кортеж
        return tuple([instance_to_dict(index) for index in instance_obj])
    elif isinstance(instance_obj, set):
        # если это множество
        return {instance_to_dict(index) for index in instance_obj}
    elif isinstance(instance_obj, dict):
        # если это словарь
        main_dict = dict()
        for index in instance_obj.keys():
            main_dict.update({index: instance_to_dict(instance_obj[index])})
        return main_dict
    elif isinstance(instance_obj, (basestring, long, int, float)):
        # если это строка или число
        return instance_obj
    elif instance_obj is None:
        # если это None
        return instance_obj
    else:
        raise AssertionError("Not found type for element %s type=%s" % (str(instance_obj), str(type(instance_obj))))


def dict_to_str_for_set(data):
    """ Преобразуем словарь в строку для применения в запросе для CQL или SQL.
    Например "UPDATE wares SET <преобразованный словарь> WHERE ware_id=56;"
    Все ключи и строки в ковычках, None заменям на Null.
    :param data: словарь с данными
    :return: строка
    """

    null = lambda t: "'%s' = Null" % t
    b_str = lambda k1, v1: "'%s' = '%s'" % (k1, v1)
    no_str = lambda k2, v2: "'%s' = %s" % (k2, v2)
    sr = lambda k, v: b_str(k, v) if isinstance(v, basestring) else null(k) if v is None else no_str(k, v)
    new_str = str()
    for num, index in enumerate(data.items()):
        if num == 0:
            new_str = sr(index[0], index[1])
        else:
            new_str = new_str + "," + sr(index[0], index[1])
    return new_str


def get_an_error(funct, *params):
    """ Ожидаем получить ошибку.
    Например потому что элемент не должн быть найден.
    :param funct: исполняемая функция
    :param params: параметры к исполняемой функции
    :return:
    """
    tx = None
    try:
        funct(*params)
    except Exception, tx:
        service_log.put("Expected error - successful!")
        service_log.put("Error: %s" % str(tx))
        return True
    service_log.error("Not found error!")
    assert AssertionError("Not found error!")


def NoneToInt(val):
    """ Если значение None, конвертим его в 0.
    :param val: значение
    :return: 0 или число
    """
    if val is None:
        return 0
    elif isinstance(val, int):
        return val
    else:
        service_log.error("Value is not int or None")
        assert AssertionError("Value is not int or None")


def round_unix_to_sec(tk):
    """ Округление unix-времени до секунд.
    Пример: 1428410576941 -> 1428410577
    :param tk: unix-время, type(long)
    :return: округленное unix-время, type(long)
    """
    ntk = int(round(float("%s.%s" % (tk[:-3], tk[-3:]))))
    service_log.put("Round the UNIX time to seconds, source=%s -> convert=%s." % (tk, ntk))
    return ntk


def crop_unix_time_to_sec(ut):
    """ Обрезаем unix-время до секунд.
    Пример: 1428410576941 -> 1428410576
    :param ut: unix-время
    :return: строка со временем
    """
    if len(str(ut)) == 13:
        return "%s" % str(ut)[:-3]
    else:
        msg = "No match long string containing the unix-time, %s " % str(ut)
        raise AssertionError(msg)


def crop_date_time_to_sec(dt):
    """ Обрезаем время до секунд.
    Пример: 2015-04-07 12:42:56.941000 -> 2015-04-07 12:42:56
    :param dt: unix-время
    :return: строка со временем
    """
    if len(str(dt)) == 26:
        return str(dt).split(".")[0]
    else:
        msg = "No match long string containing the date-time, %s " % str(dt)
        raise AssertionError(msg)


def time_to_unix(tmc):
    """ Конвертировать время в unix.
    Пример: 2015-04-07 12:42:56 -> 1428410576
    :param tmc: время
    :return: строка в формате unix-времени
    """
    return str("%s" % int(time.mktime(time.strptime(tmc, '%Y-%m-%d %H:%M:%S'))))


def unix_to_time(utt):
    """ Конвертировать unix-время в обычный формат времени.
    Пример: 1428410576 -> 2015-04-07 12:42:56
    :param utt: unix-время
    :return: строка со временем
    """
    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(float(utt))))


def crop_and_convert_time_to_unix(source):
    """ Обрезаем строка до секунд и конвертируем время в формат unix.
    :param source: исходное время
    """
    return time_to_unix(crop_date_time_to_sec(source))


def crop_and_convert_unix_to_time(source):
    """ Обрезаем строка до секунд и конвертируем время в формат unix.
    :param source: исходное время в формат unix
    """
    return unix_to_time(crop_unix_time_to_sec(source))


def convert_none_to_pass(param):
    """
    Преобразуем None в пустое значение
    """
    p = {None: '', '': ''}
    return p[param]