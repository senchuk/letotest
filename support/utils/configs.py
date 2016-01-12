# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
#--------------------------------------------------------------------
#         	Настройка конфигов.
#--------------------------------------------------------------------
__author__ = 's.trubachev'

import ConfigParser
import os


class InitializationConfigs():
    import sys
    import os
    path = os.getcwd()
    opsys = sys.platform
    if 'win32' == opsys.lower() or 'win64' == opsys.lower():
        SEP = '\\'
    else:
        SEP = '/'
    LOGGER_CONFIG = "%sconfigs%smain.cfg" % (SEP, SEP)
    ENV_CONFIG = "%sconfigs%senv.cfg" % (SEP, SEP)

    def __init__(self, log):
        # Read main config file
        self.config = {}
        config_raw = ConfigParser.ConfigParser()
        log.put("try to get main configuration")
        config_raw.read(InitializationConfigs.path + InitializationConfigs.LOGGER_CONFIG)
        log.put("sections are %s" % config_raw.sections())
        self.config.update(dict(config_raw.items('default')))
        self.config["frontend"] = dict(config_raw.items('frontend'))
        self.config["backend"] = dict(config_raw.items('backend'))
        self.config["system_settings"] = dict(config_raw.items('system_settings'))
        self.config["repository"] = dict(config_raw.items('repository'))
        self.config["path_repository"] = dict(config_raw.items('path_repository'))
        self.config["thrift_variables"] = dict(config_raw.items('thrift_variables'))
        self.config["prefix"] = dict(config_raw.items('prefix'))
        self.config["mobile"] = dict(config_raw.items('mobile'))

        # Update environment from ENV variables if exists
        env = os.environ.get('ENV', None)
        if env:
            self.config["env"] = env

        # read environments configuration
        log.put("try to get environments configuration")
        config_raw.read(InitializationConfigs.path + InitializationConfigs.ENV_CONFIG)

        # Логируем переменные конфигурации
        self.config["env_info"] = dict(config_raw.items(self.config["env"]))
        log.put("Environment scheme: [%s]" % self.config["env"])
        log.put("variables in env: %s" % self.config["env_info"])

    def get_cfg(self):
        return self.config
