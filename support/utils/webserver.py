# -*- coding: utf-8 -*-


__author__ = 'Strubachev'

import socket
import threading
import time
from support import configs, service_log
from argparse import ArgumentError


class WebServer(threading.Thread):

    def __init__(self, response=None):
        threading.Thread.__init__(self)
        self.host = (configs.config["env_info"]["serv_url"]).replace("http://", '')
        self.port = int(configs.config["env_info"]["serv_port"])
        self.timeout_server = configs.config["system_settings"]["sys_timeout_listen_port"]
        self.count_connect = configs.config["system_settings"]["sys_count_connect_for_serv"]
        self.info_requests = list()
        self.stop_server = False
        self.response = response

    def run(self):
        """ Старт Веб-сервера """
        self.StartServer(self.host, self.port, self.response)

    def StartServer(self, host='localhost', port=83, response=None):
        """ Веб-сервера для автотестов.
        Сервер работает в отдельном потоке.
        Информацию предоставляет через глоб.переменную info_requests.
        :param host: ip адрес
        :param port: номер порта
        :param response: response server
        :return: ничего или вызываем exception
        """
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        print "port %s opened" % port
        start_timer = None
        try:
            while self.stop_server is False:
                server.settimeout(float(self.timeout_server))  # Таймаут для прослушки порта
                server.listen(int(self.count_connect))     # Случшаем порт
                service_log.put("Socket open!")
                sock, user = server.accept()
                service_log.put("Server accept")
                service_log.put("Server socket: %s" % str(sock))
                service_log.put("Server user: %s" % str(user))
                service_log.warning("A non-blocking socket operation...")

                # A non-blocking socket operation could not be completed immediately
                time.sleep(1)

                # точка для дополнительного прерывания
                start_timer = int(time.time())

                data = sock.recv(1024).split("\r\n")        # считываем запрос и бьём на строки

                service_log.put("Request data: %s" % data)
                method, url, proto = data[0].split(" ", 2)  # обрабатываем первую строку
                headers = {}
                pos = None
                for pos, line in enumerate(data[1:]):  # проходим по строкам и заодно запоминаем позицию
                    if not line.strip():               # пустая строка = конец заголовков, начало тела**
                        break
                    key, value = line.split(": ", 1)   # разбираем строку с заголовком
                    headers = value.lower()            # приводим ключ к "нормальному", регистронезависимому виду

                # готовим инфу по тому ответу, которую получили с порта
                info_req = {'host': host, 'port': port,
                            'method': method, 'url': url, 'proto': proto,
                            'body': data[pos+2]}
                service_log.put("Add request: %s" % info_req)
                self.info_requests.append(info_req)
                self.info_requests = self.info_requests

                # Ответ сервера
                sock.send("HTTP/1.0 200 OK\r\n")           # мы не умеем никаких фишечек версии 1.1,поэтому будем честны
                sock.send("Server: OwnHands/0.1\r\n")      # Заголовки
                sock.send("Content-Type: text/plain\r\n")  # разметка тут пока не нужна, показываем всё как есть
                sock.send("\r\n")                          # Кончились заголовки, всё остальное - тело ответа
                if response is None:
                    sock.send("Wake up, Neo…\nThe Matrix has you…\nFollow the white rabbit.\nKnock, knock, Neo.\n")
                    service_log.put("Matrix Response server done.")
                else:
                    # TODO: передавать в качестве response ссылку на метод, который
                    # todo: обрабатывает serv.info_requests и на основе него выдаёт ответ
                    service_log.put("Response server done.")
                    sock.send(response)

                service_log.put("Close socket..")
                sock.close()  # TODO: не закрывать порт, пока не получимм все пакеты
                service_log.put("Socket closed!")

                # прерывание цикла
                if int(time.time()) - start_timer > self.timeout_server:
                    service_log.error("The server timeout is exhausted!")
                    self.info_requests.append({"Error": "The server timeout is exhausted"})
                    break

        except socket.timeout:
            msg = 'Socket timeout is limited, timeout=%s sec.'
            service_log.put(msg)
            self.info_requests.append({'Disconnect': msg % self.timeout_server})
            self.info_requests = self.info_requests
        except Exception, tx:
            service_log.put(str(tx))
            self.info_requests.append({'Error': str(tx)})
            self.info_requests = self.info_requests


def get_response_by_WebServer(serv, count=1):
    """ Получаем данные от Веб-сервера.
    Метод вернёт управление по таймауту сервера или при получении всех данных
    :param serv: объект сервера
    :param count: количество принятых пакетов
    :return: информация о полученном пакете.
    """
    full_answer = None
    run_time = int(configs.config["system_settings"]["sys_timeout_listen_port"])
    start_timer = int(time.time())
    while True:
        try:
            full_answer = serv.info_requests
            if len(full_answer) >= count or ('Disconnect' or 'Error') in full_answer[0].keys():
                serv.stop_server = True
                #serv.setDaemon(True) # вырубить демон
                return serv.info_requests
            elif "Error" in full_answer[0]:
                raise AssertionError("Server return error: %s" % str(full_answer[0]["Error"]))
            elif full_answer[0]['Disconnect']:
                break
        except IndexError:
            pass
        except KeyError:
            pass

        # прерывание цикла
        if int(time.time()) - start_timer > run_time:
            service_log.error("Timeout!")
            break
    p_error = str(full_answer[0]["Disconnect"]) if len(full_answer) != 0 else ""
    raise AssertionError("Server return error: %s" % p_error)


def start_WebServer(method_for_req=None):
    """ Делаем из потока демон, для отвязки потока от теста.
    :return: объект сервера
    """
    serv = WebServer(method_for_req)
    serv.setName('PyWebServerAutotests')
    serv.setDaemon(True)
    serv.start()
    return serv