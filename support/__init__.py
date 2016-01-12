# -*- coding: utf-8 -*-

from support.utils.configs import InitializationConfigs
from support.utils.logger import LoggerInfo, InitializationLogger
from support.utils.screenshot import InitializationScreenShot

#from argparse import ArgumentError
#import json
#from support.utils.repository import GetUrlRepository
#from support.utils.request import InitializationRequest
#from support.utils.variables import GetVariableRabbitMQ, GetVariableService, GetVariableThrift
#from support.utils.rabbit import RabbitMQ

__author__ = 'senchuk'

# Определяем логирование
logger = InitializationLogger().get_logger()
service_log = LoggerInfo(logger)

# Определяем конфигурацию
configs = InitializationConfigs(service_log)

#send_request = InitializationRequest(config)
#rabbit_variables = GetVariableRabbitMQ(config)
#service_variables = GetVariableService(config)
#thrift_variables = GetVariableThrift(config)
#rabbit = RabbitMQ()
#repository = GetUrlRepository(configs)

__all__ = ['data_generator', 'edit_config']



