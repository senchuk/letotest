# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Класс работы с протоколом Thrift.
#--------------------------------------------------------------------

from support import service_log, configs
from support.utils.variables import TVariables
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

__author__ = 'Strubachev'


class ClassThrift():
    # TODO: добавить распараллеливания
    NAME_TYPE_TRANSPORT = ["tframed", "tbuff"]

    def __init__(self):
        pass

    def __getattr__(self, item):
        if item in TVariables.thrift.workers:
            # воркер входит в списк воркеров
            global prefix_serv
            prefix_serv = item
            return ClassThrift()
        elif item in configs.config['backend']:
            # path входит в список path для backend
            global path_serv
            path_serv = item
            return ClassThrift()
        elif item in ClassThrift.NAME_TYPE_TRANSPORT:
            # определяем тип транспорта для протокола
            prefix_serv = self.import_libs(prefix_serv)
            return self.connect_to_service(path_serv=path_serv, ttype=item)
        elif item == "close":
            # закрываем соединение
            return self.clear_connect_to_service
        else:
            msg_prefix = "Unknown prefix for thrift=%s" % item
            service_log.error(msg_prefix)
            raise AssertionError(msg_prefix)

    def import_libs(self, name_prefix):
        try:
            # Производим динамический импорт сгенериррованных файлов для Thrift
            path = TVariables.thrift.imports[name_prefix + "_worker"]
            service_log.put("Get path by worker: %s" % path)
            get_lib = lambda path_lib: path_lib[path_lib.rfind(".")+1:]
            self.worker = __import__(path, fromlist=[get_lib(path)])
            service_log.put("Import libs worker: path=%s, name=%s" % (path, get_lib(path)))
            return name_prefix
        except ImportError, tx:
            error_message = "Import lib for worker - %s" % tx
            service_log.error(error_message)
            raise AssertionError(error_message)

    def connect_to_service(self, path_serv, ttype="framed"):
        """ Устанавливаем соединение с сервисом по протоколу Thrift.
        :param ttype: тип транспорта бинарного протокола
        :return: <type client>
        """

        turl = configs.config["env_info"][prefix_serv + "_url"]
        tpath = configs.config["backend"][path_serv]
        thost = turl if path_serv == 'root' else turl + tpath
        tport = configs.config["env_info"][prefix_serv + "_port"]

        try:
            # Если соединение уже было установленно, используем его
            #if 'thrift_transport' not in globals():
            #    global thrift_transport
            thrift_transport = None
            socket = TSocket.TSocket(thost, tport)
            service_log.put("Make socket: %s" % socket)
            if ttype == "tframed":
                thrift_transport = TTransport.TFramedTransport(socket)
                service_log.put("Create TFramedTransport: %s" % thrift_transport)
            elif ttype == "tbuff":
                # Делаем буферизацию. Работа с сокетами очень медленная.
                thrift_transport = TTransport.TBufferedTransport(socket)
                service_log.put("Create TBufferedTransport: %s" % thrift_transport)
                service_log.put("Buffering is critical. Raw sockets are very slow.")
            else:
                error_message = "Is not a valid binary protocol type"
                service_log.put(error_message)
                raise AssertionError(error_message)

            # Делаем врапер для протокола
            protocol = TBinaryProtocol.TBinaryProtocol(thrift_transport)
            service_log.put("Wrap in a protocol.")

            # Создаём клиента для работы с протоклом декодирования
            client = self.worker.Client(protocol)
            service_log.put("Create a client to use the protocol encoder.")

            # Коннектимся
            thrift_transport.open()
            service_log.put("Transport - open. Connect!")
            service_log.put("Control is returned to the method to call.")
            return client
        except Thrift.TException, tx:
            service_log.error(tx.message)

    @staticmethod
    def clear_connect_to_service():
        """ Закрываем соединение.
        """
        try:
            if 'thrift_transport' in globals():
                globals()['thrift_transport'].close()
                del globals()['thrift_transport']
                del globals()['prefix_serv']
                del globals()['path_serv']
                service_log.put("Transport - close.")
            else:
                service_log.put("Warning: The connection is already closed.")
        except Thrift.TException, tx:
            service_log.error(tx.message)

services = ClassThrift()



