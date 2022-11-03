import pathlib
import os
import sys

import enig


class Configuration (enig.Singleton):
    def __init__(self, yam_file: str = "./config.yml"):

        self.config_file =yam_file
        self.config = enig.cls_dict(enig.load_from_yam_file(yam_file))
        self.config.__data__ = enig.combine_agruments(self.config.__data__)
        self.working_dir = str(pathlib.Path(__file__).parent.parent)

        # self.config.__data__ = enig.combine_os_variables(self.config.__data__)
        self.static_dir = self.__get_static_dir__()

    def test(self):
        print("OK")
    def reload(self):
        self.config = enig.cls_dict(enig.load_from_yam_file(self.config_file))
        self.config.__data__ = enig.combine_agruments(self.config.__data__)
        self.working_dir = str(pathlib.Path(__file__).parent.parent)

        self.config.__data__ = enig.combine_os_variables(self.config.__data__)
        self.static_dir = self.__get_static_dir__()

    def get_value_by_key(self, key):
        ret = self.config.__data__.get(key)
        lst = list(ret.items())
        for k, v in lst:
            if ret.get(k) is None or (isinstance(ret.get(k), str) and ret.get(k).__len__() == 0):
                del ret[k]
        return ret

    def get_root_url(self):
        ret = f"{self.config.host_schema}://{self.config.host_name}"
        if self.config.host_port is not None:
            ret = f"{ret}:{self.config.host_port}"
        return ret

    def __get_static_dir__(self):
        ret = self.config.static_dir
        if ret[0:2][0:2] == "./":
            ret = ret[2:]
            ret = os.path.join(self.working_dir, ret).replace('/', os.sep)
        return ret
