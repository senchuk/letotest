# -*- coding: utf-8 -*-
import os
import shutil

__author__ = 'm.senchuk'


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = HERE[:HERE.find('support')]  # корень относительно папки "support"
LOCAL_TEMP = ROOT_PATH + 'tmp'


class InitializationScreenShot():
    SCREEN_FOLDER = LOCAL_TEMP + '/screenshot'

    def __init__(self):
        dirs = (d for d in os.listdir(InitializationScreenShot.SCREEN_FOLDER)
                if os.path.isdir(d))
        list(map(shutil.rmtree, dirs))

    @staticmethod
    def create_dir(data, str_date):
        dir_screen = InitializationScreenShot.SCREEN_FOLDER + "/" + data._testMethodName + "_" + str_date
        os.mkdir(dir_screen)
        return dir_screen