class Config:
    def __init__(self, config_dir: str, logger_name, log_dir=None):
        """
        Init configuration from configuration dir
        :param config_dir:
        """

        if not os.path.isdir(config_dir):
            raise Exception(f"'{config_dir}' was not found")

        self.config_dir = config_dir
        if not log_dir:
            self.full_path_to_log = os.path.join(config_dir, "logs").replace('/', os.sep)
            if not os.path.isdir(self.full_path_to_log):
                os.makedirs(self.full_path_to_log, mode=0o777)
        else:
            self.full_path_to_log = log_dir
        self.full_path_to_log = os.path.join(self.full_path_to_log, "log.txt")
        from fastapi.logger import logger
        self.logger = logging.getLogger("app")
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s : %(__name__)s : %(message)s')
        print(f"Api log file '{self.full_path_to_log}'")
        file_handler = logging.FileHandler(self.full_path_to_log)
        file_handler.setFormatter(formatter)
        if (self.logger.hasHandlers()):
            self.logger.handlers.clear()
        self.logger.addHandler(file_handler)
        try:
            self.path_to_star_yaml = os.path.join(config_dir, "api_app_start.yml")
            if not os.path.isfile(self.path_to_star_yaml):
                raise Exception(f"'{self.path_to_star_yaml} was not found")
            self.master_config = self.load_yaml_file(self.path_to_star_yaml)
            self.host_yalm_path = self.master_config.get("host", None)
            if not self.host_yalm_path:
                raise Exception(f"'host' point to host configuration file was not found in '{self.host_yalm_path}'")
            if not os.path.isabs(self.host_yalm_path):
                self.host_yalm_path = os.path.join(self.config_dir, self.host_yalm_path).replace('/', os.sep)



            self.app_yaml_path = self.master_config.get("app", None)
            if not self.app_yaml_path:
                raise Exception(f"'app' point to application configuration file was not found in '{self.host_yalm_path}'")
            if not os.path.isabs(self.app_yaml_path):
                self.app_yaml_path = os.path.join(self.config_dir, self.app_yaml_path).replace('/', os.sep)
            self.broker_yaml_path = self.master_config.get("broker", None)
            if self.broker_yaml_path is None:
                raise Exception(f"'broker' point to broker server configuration file was not found in '{self.host_yalm_path}'")
            if not os.path.isabs(self.broker_yaml_path):
                self.broker_yaml_path = os.path.join(self.config_dir, self.broker_yaml_path).replace('/', os.sep)
            self.search_yaml_Path = self.master_config.get("search_engine", None)
            if self.search_yaml_Path is None:
                raise Exception(f"'search_engine' point to broker server configuration file was not found in '{self.host_yalm_path}'")
            if not os.path.isabs(self.search_yaml_Path):
                self.search_yaml_Path = os.path.join(self.config_dir, self.search_yaml_Path).replace('/', os.sep)

            self.host_dict = self.load_yaml_file(self.host_yalm_path)
            if self.is_from_os_env():
                self.db_dict = self.load_db_config_from_os()
            else:
                self.db_yaml_path = self.master_config.get("db", None)
                if not self.db_yaml_path:
                    raise Exception(f"'db' point to database configuration file was not found in '{self.host_yalm_path}'")
                if not os.path.isabs(self.db_yaml_path):
                    self.db_yaml_path = os.path.join(self.config_dir, self.db_yaml_path).replace('/', os.sep)
                self.db_dict = self.load_yaml_file(self.db_yaml_path)
            self.app_dict = self.load_yaml_file(self.app_yaml_path)
            api_url = get_arg_value('--api-url')
            if api_url is not None:
                self.app_dict['root_url']=f"{api_url}"
                self.app_dict['api_url']=f"{api_url}/api"
            self.broker_dict = self.load_yaml_file(self.broker_yaml_path)
            self.search_dict = self.load_yaml_file(self.search_yaml_Path)


            self.host = config_host()
            """
            Host configuration info
            """
            if self.is_from_os_env():
                self.host_dict =self.load_host_binding_config_from_os()
            else:
                if self.host_dict.get('binding', None) is None:
                    raise Exception(f'binding was not found in "{self.host_yalm_path}"')
                if not isinstance(self.host_dict.get('binding'), dict):
                    raise Exception(f'binding in "{self.host_yalm_path}" must have ip attribute and port attribute')

            self.host.binding.ip = self.host_dict["binding"].get("ip", None)
            self.host.binding.port = self.host_dict["binding"].get("port", None)

            if self.host.binding.ip is None:
                raise Exception(f'ip attribute in binding of "{self.host_yalm_path}" was not found')
            if self.host.binding.port is None:
                raise Exception(f'port attribute in binding of "{self.host_yalm_path}" was not found')
            self.mongodb_connection_string = ""

            self.db_yaml_path=''
            self.db = config_mongo_db(self.db_yaml_path, self.db_dict)
            self.app = config_app(self.config_dir, self.app_yaml_path, self.app_dict)
            self.broker = config_broker(self.config_dir, self.broker_yaml_path, self.broker_dict)
            self.search = config_search(self.config_dir,self.search_yaml_Path,self.search_dict)
            global __logger__
            __logger__ = self.logger
            self.logger.info("-------------------------")
            self.logger.info(self.host_dict)
            self.logger.info("-------------------------")
            self.logger.info("-------------------------")
            self.logger.info(self.app_dict)
            self.logger.info("-------------------------")
            self.logger.info("-------------------------")
            self.logger.info(self.db_dict)
            self.logger.info("-------------------------")
            self.logger.info("------------------------------------------")
            self.logger.info("------------------------------------------")

        except Exception as e:
            self.logger.debug(traceback.format_exc())
            raise e

    def load_yaml_file(self, yaml_file) -> dict:
        if not os.path.isfile(yaml_file):
            raise FileNotFoundError(f"{yaml_file} was not found")
        with open(yaml_file, mode='r', encoding='utf-8') as stream:
            ret = yaml.safe_load(stream)
        if not ret:
            ret = {}
        return ret

    def is_from_os_env(self):
        return os.getenv('file_server_use_os_config') is not None

    def load_db_config_from_os(self):
        db_host = os.getenv('file_server_db_host')
        db_port = os.getenv('file_server_db_port')
        db_auth_source = os.getenv('file_server_db_auth_source')
        db_replica_set = os.getenv('file_server_db_replica_set')
        db_password = os.getenv('file_server_db_password')
        db_username = os.getenv('file_server_db_username')
        return dict(
            host= db_host,
            port= int(db_port),
            username = db_username,
            password=db_password,
            authSource=db_auth_source,
            replicaSet=db_replica_set,
            authMechanism= "SCRAM-SHA-1"
        )

    def load_host_binding_config_from_os(self):
        """
        export file_server_bind_port ='8011'
        export file_server_bind_ip ='0.0.0.0'
        :return:
        """
        return dict(
            binding=dict(
                ip=os.environ.get('file_server_bind_ip','0.0.0.0'),
                port=int(os.getenv('file_server_bind_port'))
            )
        )