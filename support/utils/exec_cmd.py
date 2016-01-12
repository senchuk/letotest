# -*- coding: utf-8 -*-
#--------------------------------------------------------------------------
#         	Класс для работы с консолью для различных операционных систем.
#--------------------------------------------------------------------------
import codecs
import platform
import subprocess
import time
from support import service_log
from support import configs

__author__ = 'Strubachev'


def wrap_platform(func):
    """ Обертка определяющая для какой ОС нужно вызвать метод.
    :type func: функция, которую оборачиваем
    :return: ссылка на функцию
    """
    def modify(*args, **kwargs):
        try:
            platform_name = CmdWork.get_platform()
            link_func = None
            if platform_name == "windows":
                link_func = CmdWindows.__dict__[func.func_name]
            elif platform_name == "linux":
                link_func = CmdLinux.__dict__[func.func_name]
            else:
                raise AssertionError("Not found name platform!")
            return link_func(*args, **kwargs)
        except Exception, tx:
            service_log.error(tx)
            raise AssertionError(tx)
    return modify


class CmdWindows():

    """ Работа с командной строкой windows. """

    def __init__(self):
        pass

    @staticmethod
    def command_exec(cmd, flag=False):
        """ Выполнить комманду через консоль.
        :param cmd: комманда для выполнения
        :param flag: флаг, дожидаться ли завершения выполнения комманды
        :return: ссылка на Popen
        """
        service_log.put("Command execute: %s" % cmd)
        pipe = subprocess.PIPE
        s_process = subprocess.Popen(cmd, shell=True, stdin=pipe, stdout=pipe, stderr=subprocess.STDOUT)

        if flag:
            s_process.wait()
        return s_process

    def kill_pid(self, pid):
        """ Убить процесс.
        :param pid: персональный идентификатор
        :return: команда
        """
        if isinstance(pid, int):
            cmd = "taskkill /PID %s" %pid
            return self.command_exec(cmd)
        else:
            assert "Error: Number PID is not integer!"

    @staticmethod
    def conversion_tasklist(input):
        """ Преобразование вывода команды tasklist в список словарь с результатами.
        :param input: входные данные
        :return: список словарей
        """
        result_list = input[input.rfind("=") + 1:].split('\r\n')
        result_crop = [index.split() for index in result_list if bool(len(index))]
        p = ["name", "pid", "name_session", "num_seance", "size"]
        convert_dict = lambda elem: dict(zip(p, [str(elem[0]), int(elem[1]), str(elem[2]), int(elem[3]), int(elem[4])]))
        result = map(convert_dict, result_crop)
        return result

    def command_tasklist(self, cmd):
        """ Работа с функцией командной строки tasklist.
        :param cmd: команда
        :return: результат команды
        """
        service_log.put("Command: %s" % cmd)
        p = self.command_exec(cmd, True)
        if p.stdout is not None:
            output = p.stdout.read()
            output = output.decode("cp866")
            service_log.put(" Output stdout: %s" % output.decode('utf-8'))
            msg1 = 'Информация: Задачи, отвечающие заданным критериям, отсутствуют.'
            if output.find(msg1) != -1:
                service_log.put("Результат поиска: задачи не найдены")
                return False
            result = self.conversion_tasklist(output)
            return result
        else:
            return False

    def find_pid_by_title(self, title):
        """ Найти PID по заголовку окна.
        :param title: заголовок окна
        :return:  список словарей
        """
        cmd = 'tasklist /FI "WINDOWTITLE eq %s"' % title
        return self.command_tasklist(cmd)

    def find_process_by_name(self, image_name):
        """ Найти процесс по названию его образа.
        :param image_name: название процесса
        :return: вывод команды
        """
        cmd = 'tasklist /FI "IMAGENAME eq %s"' % image_name
        return self.command_tasklist(cmd)

    def start_appium(self):
        """ Запустить GUI Appium.
        Вытягиваем из конфига main.cfg путь до Appium и стратуем через консоль.
        P.S: http://www.guru99.com/introduction-to-appium.html
        """
        appium = configs.config["mobile"]["windows_path_appium"]
        cmd = "%s\\appium.exe" % appium
        self.command_exec(cmd, False)
        return True

    def start_cmd_appium(self):
        """ Запустить Appium через скрипт в консоле.
        Вытягиваем из конфига main.cfg путь до Appium и стратуем через консоль.
        P.S: http://www.guru99.com/introduction-to-appium.html
        """
        appium = configs.config["mobile"]["windows_path_appium"]
        name_machine = configs.config["env_info"]["android_name"]
        cmd = """%s\\node_modules\.bin\\appium.cmd --avd %s""" % (appium, name_machine)
        service_log.put("Command execute: %s" % cmd)
        pipe = subprocess.PIPE
        subprocess.Popen(cmd, shell=True, stdin=pipe, stdout=codecs.open("./appium_out.log", "a", encoding="utf-8"),
                         stderr=codecs.open("./appium_error.log", "a", encoding="utf-8"))
        time.sleep(10)
        return True

    def kill_cmd_appium(self):
        pass

    def start_android_emulator(self, waiting_start=30):
        """ Стартовать эмулятор Андроида.
        :param waiting_start: время ожидания старта эмулятора
        """
        name_machine = configs.config["env_info"]["android_name"]
        path = configs.config["mobile"]["windows_path_android_sdk"]
        cmd = "%s\\tools\\emulator.exe -avd %s" % (path, name_machine)
        self.command_exec(cmd, True)
        time.sleep(waiting_start)
        return True

    def kill_android_emulator(self, name="emulator-x86.exe"):
        """ Убить процесс отвечающий за Android эмулятор. """
        service_log.put("Initiated close process the Android emulator...\n")
        result = self.find_process_by_name(name)
        if not result:
            service_log.warning("Process Android emulator not found!\n")
            return False
        cmd_work.kill_pid(result[0]["pid"])
        flag = int(time.time())
        while bool(self.find_process_by_name(name)):
            # ждем 5 минут до завршения работы эмулятора
            if flag + (60*5) > int(time.time()):
                service_log.warning("Close process the Android emulator - Fail!\n")
                return False
            else:
                time.sleep(5)
        service_log.put("Close process the Android emulator - success.\n")
        return True

    def adb_start_server(self):
        """ Запустить сервер ADB для Android.
        """
        path = configs.config["mobile"]["windows_path_android_sdk"]
        cmd = path + "platform-tool\\adb start-server"
        self.command_exec(cmd, True)
        #time.sleep(30)
        return True

    def adb_stop_server(self):
        """ Выключить сервер ADB для Android.
        """
        path = configs.config["mobile"]["windows_path_android_sdk"]
        cmd = path + "platform-tool\\adb kill-server"
        self.command_exec(cmd, True)
        time.sleep(30)
        return True


class CmdLinux():

    """ Работа с командной строкой Linux. """

    def __init__(self):
        pass

    def kill_pid(self, pid):
        pass

    @staticmethod
    def find_pid_by_title(title):
        pass

    @staticmethod
    def find_process_by_name(image_name="emulator-x86.exe"):
        pass


class CmdWork(CmdWindows, CmdLinux):

    """ Работа с командной строкой. """

    @staticmethod
    def get_platform():
        """ Метод определяет операционную систему (ОС).
        :return: название ОС
        """
        return "windows" if platform.uname()[0] == "Windows" else "linux"

    @wrap_platform
    def kill_pid(*kwargs, **args):
        """ Убить процесс. """
        pass

    @wrap_platform
    def find_process_by_name(*kwargs, **args):
        """ Найти процесс по названию его образа. """
        pass

    @wrap_platform
    def find_pid_by_title(*kwargs, **args):
        """ Найти PID по заголовку окна. """
        pass

    @wrap_platform
    def kill_android_emulator(*kwargs, **args):
        """ Убить процесс Android-эмулятора. """
        # todo: http://stackoverflow.com/questions/5912403/how-to-shut-down-android-emulator-via-command-line
        # todo: использовать команду: adb emu kill
        pass

    @wrap_platform
    def start_appium(*kwargs, **args):
        """ Запустить Appium.
        P.S: http://www.guru99.com/introduction-to-appium.html
        """
        pass

    @wrap_platform
    def start_android_emulator(*kwargs, **args):
        """ Запустить Android эмулятор. """
        pass

    @wrap_platform
    def adb_start_server(self):
        """ Запустить ADB сервер для работы с Android. """
        pass

    @wrap_platform
    def adb_stop_server(self):
        """ Остановить ADB сервер для работы с Android. """
        pass

    @wrap_platform
    def start_cmd_appium(self):
        """ Запустить Appium через скрипт в консоле. """
        pass

    @wrap_platform
    def kill_cmd_appium(self):
        """ Запустить Appium через скрипт в консоле. """
        pass

cmd_work = CmdWork()

