import threading

import enig
import enig_frames.config
import logging
import pathlib
import os


class Loggers(enig.Singleton):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 )):
        self.working_dir = str(pathlib.Path(__file__).parent.parent)
        self.configuration: enig_frames.config.Configuration = configuration
        self.lock = threading.Lock()
        self.cache = {}

    def get_logger(self, logger_name: str = "main", logger_dir: str = "./logs") -> logging.Logger:

        if logger_dir[0:2] == "./":
            logger_dir = logger_dir[2:logger_dir.__len__()]
            logger_dir = os.path.join(self.working_dir, logger_dir)

        if self.cache.get(logger_name) is not None:
            return self.cache.get(logger_name)
        self.lock.acquire()
        try:
            # create logger for prd_ci
            log = logging.Logger(logger_name)
            # log.setLevel(level=logging.INFO)

            # create formatter and add it to the handlers
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            full_log_dir = os.path.join(logger_dir, logger_name)
            if not os.path.isdir(full_log_dir):
                os.makedirs(full_log_dir)

            info_handler = logging.FileHandler(os.path.join(full_log_dir, "log.txt"))
            info_handler.setFormatter(formatter)

            log.addHandler(info_handler)
            self.cache[logger_name] = log
            return log
        finally:
            self.lock.release()
