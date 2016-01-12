# -*- coding: utf-8 -*-
from selenium.webdriver.remote.command import Command

__author__ = 'senchuk'


class SeleniumMethods():

    @staticmethod
    def get_local_storage_keys(driver):
        """
        Gets the local storage keys list.

        :Usage:
            driver.local_storage_keys
        """
        return driver.execute(Command.GET_LOCAL_STORAGE_KEYS)['value']

    @staticmethod
    def get_local_storage_items(driver, key):
        """
        Gets the local storage item by key.

        :Usage:
            driver.local_storage_items('local_key')
        """
        return driver.execute(Command.GET_LOCAL_STORAGE_ITEM, {'key': key})['value']

    @staticmethod
    def get_all_cookies_items(driver):
        """ Gets the all cookies.
        """
        return driver.execute(Command.GET_ALL_COOKIES)

    @staticmethod
    def get_cookies_item(driver, key):
        """ Gets the cookies by key.
        """
        # TODO: Not found command in selenium
        return driver.execute(Command.GET_COOKIE, {'key': key})['value']



