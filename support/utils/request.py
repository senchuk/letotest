# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс работы с запросами.
#--------------------------------------------------------------------
import json
import requests
import support as ss

__author__ = 'Strubachev'


class InitializationRequest():
    """ Инициализация запроса к сервису.
    Пример обращения для отправки запроса: send_request.gf.filterfacade.rpc(params),
    где gf - название сервиса и его префикс, filterfacade - это path в url,
    rpc - вызываемый метод, params - параметры запроса
    """

    def __init__(self, cfg):
        """ Инициализация работы с запросами.
        :param cfg: ссылка на конфигурацию
        """

        # Определяем переменные конфигурации
        self.cfg = cfg
        self.env_cfg = cfg["env_info"]
        self.backend_cfg = cfg["backend"]

        try:
            # Находим все префиксы и path
            name_url_variables = [index for index in self.env_cfg.keys() if index.find("url_") == 0]
            self.array_prefix = [index.replace("url_", "") for index in name_url_variables]
            self.array_path = self.backend_cfg
        except:
            msg_any_pref = "Unknown any prefix in env.cfg"
            ss.service_log.error(msg_any_pref)
            raise AssertionError(msg_any_pref)

    def __getattr__(self, item):
        # делаем привязку к сервису
        if item in self.array_prefix:
            global prefix_serv
            prefix_serv = item
            return InitializationRequest(self.cfg)
        elif item in self.array_path:
            env = self.env_cfg
            with_port = lambda i: env["url_" + i] + ':' + env["port_" + i]
            without_port = lambda i: env["url_" + i]

            # Проверяем, что есть порт и он не пуст
            if "port_"+prefix_serv in env.keys():
                self.url = with_port(prefix_serv) if env["port_" + prefix_serv] is not '' else without_port(prefix_serv)

            # Добавляем к основному url путь path
            self.url = self.url + self.backend_cfg[str(item)]

            # Делаем вызов метода отправки запроса
            return type('SendRequest', (), {"rpc": self.send_to_request_rpc,
                                            "error_rpc": self.send_to_request_error_rpc,
                                            "thrift_chanel": self.send_to_requests_thrift_framed_transport})
        else:
            msg_prefix = "Unknown prefix=%s in env.cfg" % item
            ss.service_log.error(msg_prefix)
            raise AssertionError(msg_prefix)

    def send_to_request_rpc(self, params, to_crop=True):
        """ Отсылаем запрос сервису.
        :param params: rpc-запрос
        :param to_crop: если False, то возвращать полный ответ, т.е. вместе с информацией: id, версия json
        :return: ответ сервера
        """

        msg_url = "URL service: %s" % self.url
        msg_params = "Info params for service: %s" % params

        req_result = requests.post(self.url, data=params)
        text_result = req_result.text
        crop_response = lambda d: d["result"] if to_crop is True else d
        try:
            data = None
            result = json.loads(text_result)
            if type(result) is list:
                data = [crop_response(index) for index in result]
            else:
                data = crop_response(result)
            ss.service_log.put(msg_url)
            ss.service_log.put(msg_params)
            ss.service_log.put("Reply received from service")
            return data
        except ValueError:
            ss.service_log.put(msg_url)
            ss.service_log.put(msg_params)
            if bool(self.cfg["system_settings"]["logger"]) is True:
                ss.service_log.error("Parse error in result from service: %s" % text_result)
            raise AssertionError("Parse error in result from service")

    def send_to_request_error_rpc(self, params, to_crop=True):
        """ Отсылаем запрос сервису.
        :param params: rpc-запрос
        :param to_crop: если False, то возвращать полный ответ, т.е. вместе с информацией: id, версия json
        :return: ответ сервера
        """
        msg_url = "URL service: %s" % self.url
        msg_params = "Info params for service: %s" % params

        req_result = requests.post(self.url, data=params)
        text_result = req_result.text
        crop_error_response = lambda d: d["error"] if to_crop is True else d
        try:
            data = None
            result = json.loads(text_result)
            if type(result) is list:
                data = [crop_error_response(index) for index in result]
            else:
                data = crop_error_response(result)
            ss.service_log.put(msg_url)
            ss.service_log.put(msg_params)
            ss.service_log.put("Reply received from service")
            return data
        except ValueError:
            ss.service_log.put(msg_url)
            ss.service_log.put(msg_params)
            if bool(self.config["system_settings"]["logger"]) is True:
                ss.service_log.error("Parse error in result from service: %s" % text_result)
            raise AssertionError("Parse error in result from service")

    def send_to_requests_thrift_framed_transport(self, path, type="Framed"):

        from thrift import Thrift
        from thrift.transport import TSocket
        from thrift.transport import TTransport
        from thrift.protocol import TBinaryProtocol

        a = self.url
        def start_channel():

            #transport = TSocket.TSocket(thrift_host, thrift_port)
            ss.service_log.put("OMG")

        start = start_channel
        pass

    def test(self):
        self.send_to_requests_thrift_framed_transport(1,2).start_channel()