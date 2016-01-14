# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Переопределяем методы unittest.
#       P.S: Имей совесть и делай что хочешь.
#--------------------------------------------------------------------
import unittest
import funcy
import traceback
from support import service_log, configs

__author__ = 'senchuk'

# TODO: print u"Тестирование, русские буквы в консоли windows ".encode("cp866")


def assert_log(func):
    """ Обертка для методов типа assert из unittest.
    Логируем необходимые действия.
    :type func: функция, которую оборачиваем
    :return: ссылка на функцию
    """
    def modify(*args, **kwargs):
        try:
            service_log.put("Params for %s: %s, %s" % (func.func_name, str(args[1:]), str(kwargs)))
            link_func = unittest.TestCase.__dict__[func.func_name]
            return link_func(*args, **kwargs)
        except Exception, tx:
            limit_print_exc = 10
            msg_line = "#" + ("-"*100)
            service_log.error(tx)
            service_log.put("\n%s\n%s\n%s" % (msg_line, traceback.format_exc(limit_print_exc), msg_line))
            trace_stack_log = funcy.join(traceback.format_stack(limit=limit_print_exc))
            service_log.put("Traceback stack:\n%s\n%s" % (str(trace_stack_log), msg_line))
            raise AssertionError(tx)
    return modify


class MainClass(unittest.TestCase):

    # TODO: я не зря от сюда убрал эти параметры! конфигурационные параметры должны браться только через методы!!!
    ENV_BASE_URL = None
    ENV_HOST = None

    try:
        ENV_BASE_URL = configs.config["env_info"]["front_base_url"]
        ENV_HOST = configs.config["env_info"]["front_host"]
    except Exception, tx:
        service_log.put("Warning! Not found param config: %s" % str(tx))

    @assert_log
    def assertEqual(*args, **kwargs):
        pass

    @assert_log
    def assertDictEqual(*args, **kwargs):
        pass

    @assert_log
    def assertGreaterEqual(*args, **kwargs):
        pass

    @assert_log
    def assertGreater(*args, **kwargs):
        pass

    @assert_log
    def assertLessEqual(*args, **kwargs):
        pass

    @assert_log
    def assertLess(*args, **kwargs):
        pass

    @assert_log
    def assertIsNone(*args, **kwargs):
        pass

    @assert_log
    def assertIsNotNone(*args, **kwargs):
        pass

    @assert_log
    def assertListEqual(*args, **kwargs):
        pass

    @assert_log
    def assertFalse(*args, **kwargs):
        pass

    @assert_log
    def assertTrue(*args, **kwargs):
        pass

    @assert_log
    def assertNotEqual(*args, **kwargs):
        pass
