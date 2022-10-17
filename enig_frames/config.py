import enig
class Configuration:
    def __init__(self,yam_file:str="./config.yml"):
        self.config= enig.cls_dict(enig.load_from_yam_file(yam_file))

    def get_value_by_key(self, key):
        ret= self.config.__data__.get(key)
        lst=list(ret.items())
        for k,v in lst:
            if ret.get(k) is None:
                del ret[k]
        return ret


    def get_root_url(self):
        ret = f"{self.config.host_schema}://{self.config.host_name}"
        if self.config.host_port is not None:
            ret=f"{ret}:{self.config.host_port}"
        return  ret

