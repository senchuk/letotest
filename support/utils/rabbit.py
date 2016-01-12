# -*- coding: utf-8 -*-
import json
import pika
import support
#from support import *

__author__ = 'Strubachev'

"""
rabbit_login = "guest"
rabbit_password = "guest"


class RabbitInteraction:

    rlogin = rabbit_login
    rpass = rabbit_password

    def __init__(self):
        pass

    def connect(self):
        # создаём подключение
        credentials = pika.PlainCredentials(self.rlogin, self.rpass)
        connection_params = pika.ConnectionParameters(host='www.wikimart-yml13.lan', port=5672,
                                                      virtual_host="/dataflow", credentials=credentials)
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        return channel

    def declare(self, channel, name_queue, name_exchange):
        # создать очередь (должно отправлятся в exchange), если очередь уже существует, то она не будет создана заново
        channel.queue_declare(queue=name_queue)

        # связываем exchange и очереди
        channel.queue_bind(exchange=name_exchange, queue=name_queue)
"""


class RabbitMQ():

    @staticmethod
    def init_variable(self, conf):
        self.conf = conf
        self.array_vhost = [index for index in conf["rabbitmq_virtual_hosts"]]
        self.array_queue = [index for index in conf["rabbitmq_queue"]]
        self.array_exchange = [index for index in conf["rabbitmq_exchange"]]
        return self

    @staticmethod
    def getattr_variable(self, item, new_cl_obj, cl_obj):
        if item in self.array_vhost:
            global rabbit_vh
            rabbit_vh = item
            return cl_obj(self.conf)
        elif item in self.array_queue:
            global rabbit_queue
            rabbit_queue = item
            return cl_obj(self.conf)
        elif item in self.array_exchange:
            self.rabbit_exchange = item
            return new_cl_obj
        else:
            msg_prefix = "Unknown %s in env.cfg" % item
            support.service_log.error(msg_prefix)
            raise AssertionError(msg_prefix)

    class Send():
        """
        Класс для отправка запроса в очередь.
        """
        def __init__(self, conf):
            self = RabbitMQ.init_variable(self, conf)

        def __getattr__(self, item):
            obj = type('SendRequestRabbit', (), {"rpc": self.send_request_to_rabbit})
            return RabbitMQ.getattr_variable(self, item, obj, RabbitMQ.Send)

        def send_request_to_rabbit(self, body, props=None):
            """ Отправка запроса в очередь.
            :param queue_rabbit: имя очереди
            :param body: тело очереди
            :param props: свойства запроса (pika.spec.BasicProperties)
            """
            credentials = pika.PlainCredentials(support.rabbit_variable.login, support.rabbit_variable.passwd)
            connection_params = pika.ConnectionParameters(host=support.rabbit_variable.host,
                                                          port=support.rabbit_variable.port,
                                                          virtual_host=self.conf["rabbitmq_virtual_hosts"][rabbit_vh],
                                                          credentials=credentials)

            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()
            channel.basic_publish(exchange=self.rabbit_exchange, routing_key=rabbit_queue, body=body, properties=props)
            connection.close()

    class Get():
        """
        Класс для приема запроса из очереди.
        """
        def __init__(self, conf):
            self = RabbitMQ.init_variable(self, conf)

        def __getattr__(self, item):
            obj = type('GetResponseRabbit', (), {"rpc": self.get_response_rabbit})
            return RabbitMQ.getattr_variable(self, item, obj, RabbitMQ.Get)

        def get_response_rabbit(self, queue_rabbit):
            """ Получение сообщения.
            :param queue_rabbit: имя очереди
            :return: тело сообщения
            """
            credentials = pika.PlainCredentials(support.rabbit_variable.login, support.rabbit_variable.passwd)
            connection_params = pika.ConnectionParameters(host=support.rabbit_variable.host,
                                                          port=support.rabbit_variable.port,
                                                          virtual_host=self.conf["rabbitmq_virtual_hosts"][rabbit_vh],
                                                          credentials=credentials)
            connection = pika.BlockingConnection(connection_params)
            channel = connection.channel()
            channel.queue_declare(queue=queue_rabbit, durable=True, exclusive=False, auto_delete=False)
            self.response = list()

            def callback(ch, method, properties, body):
                self.response.append(json.loads(body))
                ch.basic_ack(delivery_tag=method.delivery_tag)
                channel.stop_consuming()

            channel.basic_consume(callback, queue=queue_rabbit)
            return self.response

    def __init__(self, cfg):
        self.cfg = cfg

    def __getattr__(self, item):
        if item == "send":
            return RabbitMQ.Send(self.cfg)
        elif item == "get":
            return RabbitMQ.Get(self.cfg)



