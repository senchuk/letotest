# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#              Классы для работы с репозиториями.
#--------------------------------------------------------------------
from support import *

__author__ = 'Strubachev'


class GetUrlRepository():
    """ Склеиваем пути для репозитория.
    Пример обращения для того что бы взять полный путь до файла: repository.importer.file(<<имя файла>>)
    """

    def __init__(self, cfg):
        self.repository = cfg["repository"]["repository_url"]
        self.path_repository = cfg["path_repository"]

    def __getattr__(self, item):
        if item in self.path_repository:
            self.prefix_path = item
            return type('PathToFile', (), {"file": self.get_path_to_file})
        else:
            msg_rep = "Not found path=%s repository in main.cfg" % item
            service_log.error(msg_rep)
            raise AssertionError(msg_rep)

    def get_path_to_file(self, name_file):
        path_to_file = self.repository + self.path_repository[self.prefix_path] + name_file
        service_log.put("Get path=%s for repository" % path_to_file)
        return path_to_file
