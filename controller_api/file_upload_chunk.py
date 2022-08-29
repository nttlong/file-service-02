import quicky.object_constraints
import quicky
import os
import ReCompact_Kafka.producer
from .base_upload_progress import BaseUploadProgress
import concurrent

def __kafka_producer_delivery_report__(error, msg):
    quicky.get_app().app_config.logger.debug(error)
    quicky.get_app().app_config.logger.debug(msg)

@quicky.safe_logger()
class FileUploadChunk(BaseUploadProgress):
    """
    Upload controller
    """

    def __init__(self):
        super().__init__()
        self.full_dir_of_temp_file = ""
        self.kafka_topic = "files.services.upload"
        if not hasattr(self.app_config, "temp_dir"):
            self.app_config.logger.debug(
                f"It looks like thy forgot set 'temp_dir' in '{self.app_config.app_config_file}'"
                f"temp_dir:"
                f"     upload: <Relative Path or Absolute Path to location in that thees application"
                f"                 will push upload file>"
                f"     unzip: <Relative Path or Absolute Path to location in that thees application"
                f"                 will unzip upload file>")

    def on_upload_complete(self):
        def run_send():
            try:
                ReCompact_Kafka.producer.Bootstrap(
                    self.app_config.kafka.brokers,
                    delivery_report=__kafka_producer_delivery_report__
                ).send_msg_sync(self.kafka_topic, dict(
                    AppName=self.app_name,
                    FilePath=self.full_dir_of_temp_file,
                    UploadInfo=self.progess_info.to_dict()

                ))
            except Exception as e:
                self.app_config.logger.debug(e)
        import threading
        threading.Thread(target=run_send).start()

    def on_after_save_file_to_storage(self):
        def run_save():
            full_dir_of_app = os.path.join(self.app_config.temp_dir.upload, self.app_name)
            """
            Đường dẫn đến thư mục lưu file tạm
            """
            if not os.path.isdir(full_dir_of_app):
                os.makedirs(full_dir_of_app)
            self.full_dir_of_temp_file = os.path.join(full_dir_of_app, self.progess_info.ServerFileName)
            self.full_dir_of_temp_file=self.full_dir_of_temp_file.replace('/',os.sep)
            if not os.path.isfile(self.full_dir_of_temp_file):
                with open(self.full_dir_of_temp_file, "wb") as file:
                    file.write(self.bufer_data)
            else:
                with open(self.full_dir_of_temp_file, "ab") as file:
                    file.write(self.bufer_data)

        run_save()
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future = executor.submit(run_save, )
        #     return_value = future.result()
        #     return return_value


quicky.api_add_resource(FileUploadChunk, "/files/<app_name>/upload/chunk")
