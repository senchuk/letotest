# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Выкачиваем chromedriver.
#  Выкачивает драйвер, если он не был скачен и кладёт его в папку фреймворка.
#  P.S: Первоночальный источник: https://github.com/enkidulan/chromedriver
#--------------------------------------------------------------------
from support import service_log
from tempfile import NamedTemporaryFile
import sys
import os
import shutil
import zipfile
import platform
if sys.version_info.major == 2:
    from urllib2 import urlopen
else:
    from urllib import urlopen

__author__ = 's.trubachev'


CHROMEDRIVER_VERSION = '2.15'
DEST_FILE_NAME = 'CHROMEDRIVER'
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = HERE[:HERE.find('support')]  # корень относительно папки "support"
LOCAL_TEMP = ROOT_PATH + 'tmp'
PLATFORM_VERSION = '64' if platform.uname()[4] == 'x86_64' else '32'
PLATFORM_OS = "chromedriver_win" if platform.uname()[0] == "Windows" else "chromedriver_linux"
CHROMEDRIVER_URL_BASE = "http://chromedriver.storage.googleapis.com/%s/" + "%s%s.zip" % (PLATFORM_OS, PLATFORM_VERSION)


class RequestProgressWrapper():
    """ Simple helper for displaying file download progress;
    if works with file-like objects"""
    def __init__(self, obj):
        self.obj = obj
        self.total_size = float(obj.headers['content-length'].strip())
        self.url = obj.url
        self.bytes_so_far = 0

    def read(self, length):
        self.bytes_so_far += length
        percent = self.bytes_so_far / self.total_size
        percent = round(percent * 100, 2)
        sys.stdout.write(
            "%s: downloaded %d of %d bytes (%0.f%%)\r" %
            (self.url, self.bytes_so_far, self.total_size, percent))
        sys.stdout.flush()
        return self.obj.read(length)

    def __del__(self):
        sys.stdout.write('\n')


def download_ziped_resource(url, name):
    """ Скачать и разархивировать файл драйвера.
    Скачиваем zip-архив драйвера, распаковываем его и копируем в папку LOCAL_TEMP фреймворка.
    :param url: ссылка для скачивания драйвера
    :param name: наименование файла драйвера, которое мы установим
    :return: путь до драйвера
    """

    path_storage = os.path.join(LOCAL_TEMP, name) if platform.uname()[0] != "Windows" else \
        os.path.join(LOCAL_TEMP, name + '.exe')
    if os.path.exists(path_storage):
        service_log.put("Driver found in the store. Download terminated.")
        return path_storage
    req = urlopen(url)
    data_destination = NamedTemporaryFile(delete=False)
    with data_destination as f:
        shutil.copyfileobj(RequestProgressWrapper(req), f.file)
        f.close()  # Закрываем файл, иначе файл будет занят другим процессом
        zfile = zipfile.ZipFile(f.name, mode='r')
        zfile.extractall(LOCAL_TEMP)
        zfile.close()
        path_source_name = os.path.join(LOCAL_TEMP, zfile.namelist()[0])
        os.rename(path_source_name, path_storage)
        os.remove(f.name)

    if path_storage is None:
        msg_uninst = "The chromedriver installation process is not completed."
        service_log.put(msg_uninst)
        raise ValueError(msg_uninst)

    # Если это линукс, выставляем права на файл
    if platform.uname()[0] != "Windows":
        os.chmod(path_storage, 0o755)
    msg = "Chromedriver downloaded and can be reached by following path %s" % path_storage
    sys.stdout.write("Chromedriver downloaded and can be reached by following path %s" % path_storage)
    service_log.put(msg)
    return path_storage



CHROMEDRIVER_PATH = download_ziped_resource(CHROMEDRIVER_URL_BASE % CHROMEDRIVER_VERSION, DEST_FILE_NAME)