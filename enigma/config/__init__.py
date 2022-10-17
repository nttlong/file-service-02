import os
import pathlib
import threading
import yaml
import enigma.loggers
from kink import di, inject
import sys

__cache__ = None
__config__ = None
__lock__ = threading.Lock()
__working_dir__ = str(pathlib.Path(__file__).parent.parent.parent)
__config_path__ = None
DEFAULT_SETTINGS_CONFIG_PATH = "./config.yml"


@inject
class AppConfig:
    """
    All configuration access here. in order to use the app_config you must start app with config_path arg
    Tất cả các cấu hình phải đọc từ đây. Để sử dụng configuration phải chạy ứng dụng với tham số config_path

    """

    def __init__(self, logger: enigma.loggers.ELogger):

        self.logger: enigma.loggers.ELogger = logger
        global __cache__
        global __lock__
        global __config_path__
        if __cache__ is None:
            __lock__.acquire()
            try:
                __cache__ = {}
                for x in sys.argv:
                    if '=' in x:
                        __cache__[x.split('=')[0]] = x.split('=')[1]
                __config_path__ = self.get_sys_arg('config_path')
                if __config_path__ is None:
                    __config_path__ = DEFAULT_SETTINGS_CONFIG_PATH
                if __config_path__[0:2] == './':
                    __config_path__ = __config_path__[2:]
                    __config_path__ = __config_path__.replace('/', os.sep)
                    __config_path__ = os.path.join(__working_dir__, __config_path__)
                if not os.path.isfile(__config_path__):
                    raise Exception(f"{__config_path__} was not found")
            except Exception as e:
                self.logger.debug(e)
            finally:
                self.logger.info(f"start app with {self.config_path}")
                __lock__.release()

    @property
    def config_path(self):
        global __config_path__
        return __config_path__

    def get_sys_arg(self, key):
        global __cache__
        if __cache__.get(key):
            return __cache__[key]
        for x in sys.argv:
            if f"{key}=" in x:
                ret = x.split('=')[1]
                __cache__[key] = ret

    def get_config(self, key: str):
        global __config__
        global __lock__
        if __config__ is None:

            __lock__.acquire()
            __config__ = {}
            try:
                with open(self.config_path, 'r') as stream:
                    try:
                        __config__ = yaml.safe_load(stream)

                    except yaml.YAMLError as exc:
                        self.logger.error(exc)
            except Exception as e:
                __config__ = None
                self.logger.error(e)
            finally:
                __lock__.release()

        ret = __config__.get(key)
        if isinstance(ret, dict):
            lst = list(ret.items())
            for k, v in lst:
                if v is None:
                    del ret[k]
            __config__[key] = ret
        return __config__.get(key)
