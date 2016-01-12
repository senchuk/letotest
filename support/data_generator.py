# encoding: utf-8
import json


__author__ = 'senchuk'
import random
from argparse import ArgumentError
from support.utils import common_utils
import funcy


def alter(last_val, source):
    """ Генерировать новое значение, отличное от предыдущего.
    :param last_val: предыдущее значение
    :param source: параметры для генерации нового значение
    :return: новое значение
    """
    def loop(f, a):
        new_val = f(*a)
        while last_val == new_val:
            new_val = f(*a)
        return new_val

    if type(last_val) is list:
        if len(source) < 2:
            raise AssertionError("The source must contain more than one element")
        return loop(random.choice, source)
    elif type(last_val) is int:
        return loop(random.randint, source)
    elif type(last_val) is bool:
        return not last_val
    elif type(last_val) is str:
        return loop(common_utils.random_string, source)


def delete_duplicate(list_with_duplicate_elems):
    """ Удалить дублирующие не хешируемые элементы в списке.
    :param list_with_duplicate_elems: список
    :return: отсортированный список без дублирующих значений
    """
    source_sorted_mas = sorted(list_with_duplicate_elems, reverse=True)
    convert_elems_list = sorted(map(str, list_with_duplicate_elems), reverse=True)
    delele_elems_list = sorted(list(set(convert_elems_list)), reverse=True)
    if type(list_with_duplicate_elems) is list:
        while True:
            elem = 0
            for index, elem in enumerate(delele_elems_list):
                if elem != convert_elems_list[index]:
                    convert_elems_list.pop(index)
                    source_sorted_mas.pop(index)
                    break
            else:
                source_sorted_mas = source_sorted_mas[:len(delele_elems_list)]
            if len(source_sorted_mas) == len(delele_elems_list):
                break
    return source_sorted_mas


def create_request(method, params, ensure_ascii=False, dump=True):
    """ Создаём окончательный запрос в формате JSON.
    :param method: type(str) - наименование метода к которому посылается запрос
    :param params: type(dict) - параметры json-запроса
    """
    params = {"jsonrpc": "2.0",
              "method": method,
              "params": params,
              "id": common_utils.random_string(params="digits", length=10)}
    if dump is True:
        return json.dumps(params, ensure_ascii=ensure_ascii)
    else:
        return params


def generate_sql_list_with_params(list_params, name_value):
    """ Генерируем итеративный кусок кода для sql.
    :param list_params: список со значениями
    :param name_value: название сравниваемой переменно
    :return: кусок sql-кода (name_value=1 OR name_value=2 OR name_value=3 ...)
    """

    # если строка, оборачиваем в дополнительные ковычки
    ifstr = lambda p: "'%s'" % p if type(p) == str else "'%s'" % p

    if type(list_params) == list:
        if len(list_params) > 1:
            cur_part = ""
            for param in list_params[:-1]:
                cur_part = funcy.merge(cur_part, " %s=%s OR" % (name_value, ifstr(param)))
            cur_part = funcy.merge(cur_part, " %s=%s" % (name_value, ifstr(list_params[-1])))
            return "(" + cur_part + ")"
        elif len(list_params) == 1:
            return " %s=%s " % (name_value, ifstr(list_params[0]))
        else:
            return None
    else:
        return None


def generate_sql_list_with_params_like(list_params, name_value):
    """ Генерируем итеративный кусок кода для sql с параметром LIKE.
    :param list_params: список со значениями
    :param name_value: название сравниваемой переменно
    :return: кусок sql-кода (name_value=1 OR name_value=2 OR name_value=3 ...)
    """
    if type(list_params) == list:
        if len(list_params) > 1:
            cur_part = ""
            for param in list_params[:-1]:
                cur_part = funcy.merge(cur_part, " %s LIKE '%s' OR" % (name_value, ('%'+param+'%')))
            cur_part = funcy.merge(cur_part, " %s LIKE '%s'" % (name_value, ('%'+list_params[-1]+'%')))
            return "(" + cur_part + ")"
        elif len(list_params) == 1:
            return " %s LIKE '%s' " % (name_value, ('%'+list_params[0]+'%'))
        else:
            return None
    else:
        return None










