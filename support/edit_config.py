# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Настройка конфигурационных файлов.
#--------------------------------------------------------------------
#  - Info -
# https://github.com/Eugeny/reconfigure
# http://habrahabr.ru/post/188248/
#--------------------------------------------------------------------

__author__ = 'senchuk'

from reconfigure.parsers import NginxParser
from reconfigure.builders import BoundBuilder


class ConfiguringNginx():
    """ -------------
    ***   Nginx   ***
    ------------- """
    def __init__(self, path_to_file):
        """ Инициализация работы с конфигурационными файлами Nginx.
        Строим абстрактное синтаксическое дерево для конфигов Nginx.
        Cоздаём python-объекты и привязываем их к синтаксическому дереву.
        :params path_to_file: путь до конфигурационного файла, например: '/etc/fstab'
        """
        content = open(path_to_file).read()
        self.syntax_tree = NginxParser().parse(content)
        self.builder = BoundBuilder(NginxParser)
        self.data_tree = self.builder.build(self.syntax_tree)

    def get_data_tree(self):
        """ Взять все объекты по синтаксическому дереву.
        :return: python-объекты
        """
        return self.data_tree


