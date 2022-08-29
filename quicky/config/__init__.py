import logging
import os
import pathlib
from .. import logs
from .. import yaml_reader
from .. import logs
import yaml
from flask_restful import Resource
import traceback
import sys

class MediaConfig(object):
    def __init__(self):
        self.streaming_buffering_in_KB = 32
        """
        Khi streaming video để bảo đảm tốc độ cho ngưởi xem cần một bộ đệm RAM với dung lương là 
        8 bit * chất lương hỗ trợ ví dụ 4K thì 8*4=32KB 
        """
        self.streaming_segment_size_in_KB = 0
        """
        Streaming Segment Size: Chiều dài cho mỗi phân đoạn streaming
        Khi trình duyệt request 1 file video hoặc 1 file audio server sẽ hồi đáp lại
        một số lượng byte với kích thước  streaming_segment_size_in_KB*1024, 
        trong thời gian thiết bị đang trình chiếu nội dung, thì server fecth tiếp segment 2,..
        Chế độ giới hạn (giá trị >0):
            1 -Mặc dù ở chế độ giới hạn Segment nội dung có bị ngắt, nhưng người dùng sẽ không cảm nhận được
            2- Một số thiết bị trình chiếu nôi dung như Windows Media Player hay VLC media player, 
                hoặc các trình tải nội dung như Download manager chỉ có thể tải được Segment đầu tiên và sẽ không
                nhận được nội dung đầy đủ. Tất cả các trình duyệt Web luôn nhận đầy đủ thông tin.
        Chế độ không giới hạn (giá trị=0, đây là giá trị mặc định):
            1 - Ở chế độ này Server sẽ streaming liên tục cho đến hết nôi dung, kg ngắt quãng.
            2- Tất cả mọi thiết bị nhận được đầy đủ thông tin
            Chú ý: Ở chế độ này khi host trên IIS với FastCGI thì phải vào thư mục:
            C:\Windows\System32\inetsrv\config tìm trang applicationHost.config
            Thẻ fastCgi bổ sung thêm activityTimeout="60000" requestTimeout="60000" instanceMaxRequests="1000000"
              
        """

class ElasticSearch(object):
    def __init__(self):
        self.url =""
        """
        Url của elastic search server
        """
        self.index =""
        """
        index của Elastic Search
        """
class TempDir:
    def __init__(self):
        self.upload = "temp/upload"
        self.unzip = "temp/unzip"

class Captcha:
    def __init__(self):
        self.secret_key="FSOajYn1757FYjka2RpeeG8Li0N4KuX5"

class __Kafka__:
    def __init__(self):
        self.brokers = []


class Config:
    def __init__(self, app_file_or_folder):
        self.elastic_search =ElasticSearch()
        """
        Cấu hình elastic search
        """
        self.media = MediaConfig()
        """
        Phần cấu hình cho media
        """
        self.captcha = Captcha()
        """
        Thông tin captcha
        """
        app_file = app_file_or_folder
        if not os.path.isfile(app_file):
            if not os.path.isdir(app_file):
                raise Exception(f"{app_file} was not found")
        else:
            app_file = str(pathlib.Path(app_file).parent)
        """
        Create config form app_dir
        :param app_dir:
        """
        self.name = "Noname"
        self.description = "Create congfig.yaml and mappall quicky.config.Congfig attr to congfig.yaml"
        self.host_dir = '/'
        self.debug = True
        """
                Debug or release.It will  be overwrite by congfig.yalm
        """
        self.host = "127.0.0.1"
        self.binding = "0.0.0.0"
        self.port = None
        self.https = False
        self.api_dir = "api"
        self.api_url = "http://" + self.host + "/api"
        self.temp_dir = TempDir()
        self.kafka = __Kafka__()

        self.app_dir = str(pathlib.Path(app_file))
        """
        Current directory of web app
        Thư mục hiện hành của web app
        """
        self.app_logs_dir = os.path.join(self.app_dir, "logs")

        """
        Biến lưu đường dẫn đến thư mục log đường dẫn đầy đủ
        """
        self.template_folder = "templates"
        """
        Đường dẫn tương đối đến thư mục template
        """
        self.app_config_file = os.path.join(self.app_dir, "config.yaml")
        """
        Đường dẫn đến file cấu hình của tàn bộ app
        """
        if not os.path.isfile(self.app_config_file):
            data = {}
            for k, v in self.__dict__.items():
                if not k in ["app_dir", "app_logs_dir", "app_config_file"]:
                    if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
                        if hasattr(self, k):
                            data[k] = v
            with open(self.app_config_file, 'w', encoding='utf-8') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
            # raise FileNotFoundError(f"{self.app_config_file} was not found")
        self.static_dir = "static"
        """
        Đường dẫn đến thư mục static mặc định là static, tuy nhiên vẫn có thề điều chỉnh lại trong file congfig.yaml
        """
        self.static_url = "/static"
        """
        url gốc để truy cập static directory
        """
        self.full_static_dir = os.path.join(self.app_dir, self.static_dir)
        """
        Đường dẫn đầy đủ đến thư mục static
        """

        self.full_template_path = os.path.join(self.app_dir, self.template_folder)
        """
        Đường dẫn đầy đủ đến thư mục template
        """
        self.check_all_folder()
        self.logger = self.get_loger(__name__)
        self.load_yaml_config()
        self.full_url_root = f"http://{self.host}"

        self.full_url_static = self.full_url_root + self.static_url
        """
        Url gốc của host
        """
        if self.https:
            self.full_url_root = f"https://{self.host}"
        else:
            if isinstance(self.port, int):
                self.full_url_root = f"http://{self.host}:{self.port}"
            else:
                self.full_url_root = f"http://{self.host}"
        self.full_url_app = self.full_url_root
        if self.host_dir is not None and self.host_dir != '/':
            self.full_url_app = self.full_url_root + self.host_dir

    def get_loger(self, name) -> logging.Logger:
        logs.set_root_app_dir(self.app_dir)  # Cài đặt thư mục app cho log
        logs.set_root_dir(self.app_logs_dir)
        logger = logs.get_logger(name, self.app_dir)
        return logger

    def create_folder_if_not_exist(self, folder_path):
        if not os.path.isdir(folder_path):
            os.makedirs(folder_path)

    def check_all_folder(self):
        """
        Kiểm tra các thư mục cần thiết. nếu thiếu thì tạo
        :return:
        """
        self.create_folder_if_not_exist(self.full_template_path)
        self.create_folder_if_not_exist(self.app_logs_dir)
        self.create_folder_if_not_exist(self.static_dir)

    def load_yaml_config(self):
        yaml_data = yaml_reader.from_file(self.app_config_file)
        if yaml_data.get("use", None) is not None:
            yam_rel_Path = yaml_data["use"]
            if os.path.isabs(yam_rel_Path):
                self.app_config_file = yam_rel_Path
                self.__load_yaml_config__()
            else:
                self.app_config_dir = str(pathlib.Path(self.app_config_file).parent.absolute())
                self.app_config_file = os.path.join(self.app_config_dir, yam_rel_Path.replace('/', os.sep))
                self.__load_yaml_config__()
        else:
            self.__load_yaml_config__()

    def __load_yaml_config__(self):
        """
        Lấy thông tin từ file yaml và cài đặt lại các tham số
        :return:
        """
        exception_msg = ""
        try:
            self.meta = yaml_reader.from_file(self.app_config_file)
            for k, v in self.meta.items():
                if k=="elastic_search":
                    if isinstance(v,dict):
                        self.elastic_search.url = v.get("url",None)
                        self.elastic_search.index = v.get("index",None)
                if k == "media":
                    if isinstance(v, dict):
                        self.media.streaming_buffering_in_KB = v.get(
                            "streaming_buffering_in_KB",
                            self.media.streaming_buffering_in_KB
                        )
                        self.media.streaming_segment_size_in_KB = v.get(
                            "streaming_segment_size_in_KB",
                            self.media.streaming_segment_size_in_KB
                        )
                        continue
                elif k == "kafka":
                    if isinstance(v, dict):
                        if v.get("brokers", None) is None:
                            raise Exception(f"brokers was not found at kafka in '{self.app_config_file}'")
                        if not isinstance(v.get("brokers"), list):
                            raise Exception(f"brokers at kafka in '{self.app_config_file}' must be a list")
                        self.kafka.brokers = v.get("brokers")
                elif k == "temp_dir":
                    if isinstance(v, dict):
                        self.temp_dir.upload = v.get("upload", self.temp_dir.upload)
                        if os.path.isabs(self.temp_dir.upload):
                            if not os.path.isdir(self.temp_dir.upload):
                                raise Exception(f"directory '{self.temp_dir.upload}' was not found"
                                                f"Thy please look at '{k}.upload in '{self.app_config_file}' ")
                        else:
                            self.temp_dir.upload = os.path.join(self.app_dir, self.temp_dir.upload.replace('/', os.sep))
                            if not os.path.isdir(self.temp_dir.upload):
                                os.makedirs(self.temp_dir.upload)

                        self.temp_dir.unzip = v.get("unzip", self.temp_dir.unzip)

                        if os.path.isabs(self.temp_dir.unzip):
                            if not os.path.isdir(self.temp_dir.unzip):
                                raise Exception(f"directory '{self.temp_dir.unzip}' was not found\n"
                                                f"Thy please look at '{k}.unzip in '{self.app_config_file}' ")
                        else:
                            self.temp_dir.unzip = os.path.join(self.app_dir, self.temp_dir.unzip.replace('/', os.sep))
                            if not os.path.isdir(self.temp_dir.unzip):
                                os.makedirs(self.temp_dir.unzip)
                    continue
                elif k == "static":
                    if os.path.isabs(v):
                        if not os.path.isdir(v):
                            exception_msg = f"'{v}' was not found " \
                                            f"Thy should check static in '{self.app_config_file}'"

                            raise Exception(exception_msg)
                        self.full_static_dir = v
                    else:
                        self.full_static_dir = os.path.join(self.app_dir, v)
                        if not os.path.isdir(self.full_static_dir):
                            os.makedirs(self.full_static_dir)
                elif k == "template_folder":
                    if os.path.isabs(v):
                        if not os.path.isdir(v):
                            exception_msg = f"'{v}' was not found " \
                                            f"Thy should check template_folder in '{self.app_config_file}'"

                            raise Exception(exception_msg)
                        self.full_template_path = v
                    else:
                        self.full_template_path = os.path.join(self.app_dir, v)
                        if not os.path.isdir(self.full_template_path):
                            os.makedirs(self.full_template_path)
                elif k == "captcha":
                    if not isinstance(v,dict):
                        raise Exception(f"{v} in {self.app_config_file} at {k} is invalid\n"
                                        f"The value of {k} must be \n"
                                        f"{k}:\n"
                                        f"  secret_key:bla bla")
                    self.captcha.secret_key= v.get("secret_key",self.captcha.secret_key)
                elif hasattr(self, k):
                    setattr(self, k, v)
        except Exception as e:
            self.logger.info(exception_msg)
            raise e

    def get_route_path(self, r_path):

        if self.host_dir != '/' and self.host_dir.__len__() > 1:
            if self.host_dir[0:1] != '/':
                raise Exception(f"{self.sub_dir} must start with '/")
            return self.host_dir + r_path
        else:
            return r_path

    def logger_wrapper(self, *args, **kwargs):
        def wraper(*x, **y):
            cls = x[0]
            if issubclass(cls, Resource):
                keys = list(cls.__dict__.keys())
                for k in keys:
                    if k in ["post","get"]:
                        # if not (k.__len__() > 4 and k[0:2] == "__" and k[-2:] == "__"):
                        if hasattr(cls, k):
                            v = getattr(cls, k)
                            if callable(v):
                                setattr(cls, f"__old_{k}__", v)

                                def wrapper_handler(*a, **b):
                                    instance = a[0]
                                    print(wrapper_handler.__name__)
                                    fn_name = wrapper_handler.__name__.split('_')[3]
                                    func =None
                                    try:
                                        if hasattr(instance, f"__old_{fn_name}__"):
                                            fn = getattr(instance, f"__old_{fn_name}__")
                                            func=fn.__func__
                                            ret = fn.__func__(*a, **b)
                                            return ret
                                        else:
                                            fn = getattr(instance,fn_name)
                                            func = fn.__func__
                                            ret = fn.__func__(*a, **b)
                                            return ret
                                    except Exception as e:
                                        self.logger.debug("---------------------------------------------------------")
                                        self.logger.debug(traceback.format_exc())
                                        self.logger.debug("---------------------------------------------------------")
                                        raise Exception(traceback.format_exc())


                                wrapper_handler.__name__ = f"__wrapper_{k}__"
                                setattr(cls, k, wrapper_handler)
                return cls
            elif callable(cls):
                return cls

        return wraper
