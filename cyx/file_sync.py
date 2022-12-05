import datetime
import os.path
import pathlib
import threading
import time

import cy_docs
import cy_kit
from cyx.common.msg import MessageInfo, MessageService
from cyx.common.base import DbConnect
from cyx.models import FsFile, FsChunks
from cyx.media.image_extractor import ImageExtractorService
import bson
from typing import List


class FilesSync:
    def __init__(
            self,
            db_connect: DbConnect = cy_kit.singleton(DbConnect),

            message_service: MessageService = cy_kit.singleton(MessageService)
    ):

        self.message_service = message_service
        self.db_connect: DbConnect = db_connect
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.file_dir = os.path.join(self.working_dir, "background_service_files", "file")
        self.logs_dir = os.path.join(self.working_dir, "background_service_files", "logs")
        if not os.path.isdir(self.file_dir):
            os.makedirs(self.file_dir, exist_ok=True)
        if not os.path.isdir(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)
        self.logs = cy_kit.create_logs(self.logs_dir, FilesSync.__name__)
        self.logs.info(
            f"start service {FilesSync.__name__}"
        )

    def sync_file(self, item: MessageInfo):
        upload_id = item.Data.get("_id")
        upload_item = cy_docs.DocumentObject(item.Data)

        if not upload_item:
            return
        file_ext = upload_item.FileExt
        full_file_path = os.path.join(self.file_dir, f"{upload_id}.{file_ext}")
        if os.path.isfile(full_file_path):
            return full_file_path
        file_id = upload_item.MainFileId

        current_chunk_index = 0
        num_of_chunks = upload_item.NumOfChunks

        start_time = datetime.datetime.utcnow()

        self.logs.info(f"start sync file {full_file_path} at {datetime.datetime.utcnow()}")

        try:
            timeout_count = 0
            _file_id = file_id
            if isinstance(file_id, str):
                _file_id = bson.ObjectId(file_id)
            chunk_context = self.db_connect.db(app_name=item.AppName).doc(FsChunks)
            while current_chunk_index < num_of_chunks:
                chunk = chunk_context.context @ ((chunk_context.fields.files_id == _file_id) & (
                            chunk_context.fields.n == current_chunk_index))

                if timeout_count > 1000:
                    self.logs.info(f"sync file {full_file_path} fail, timeout {timeout_count / 2} senconds")
                    os.remove(full_file_path)

                    return
                if chunk is None:
                    time.sleep(0.5)
                    timeout_count += 1

                else:
                    data = chunk.data
                    if not os.path.isfile(full_file_path):
                        with open(full_file_path, "wb") as f:
                            f.write(data)
                        del data
                    else:
                        with open(full_file_path, "ab") as f:
                            f.write(data)
                        del data
                    current_chunk_index += 1
                time.sleep(0.001)
            total_seconds = (datetime.datetime.utcnow() - start_time).total_seconds()
            self.logs.info(f"sync file {full_file_path} complete in {total_seconds} second")
            return full_file_path
        except Exception as e:
            self.logs.exception(e)

    def sync_file_in_thread(self, item: MessageInfo, handler_service, output: dict, use_thread = True):
        output = dict()
        def run(_output: dict):
            _output = {}
            try:
                full_file_path = self.sync_file(item)
                handler_service.resolve(item,full_file_path)



            except Exception as e:
                output["error"] =e
                self.logs.exception(e)

        if use_thread:
            th_run = threading.Thread(target=run, args=(output,)).start()
            return th_run
        else:
            run(output)
