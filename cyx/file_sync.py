import datetime
import os.path
import pathlib
import threading
import time

import bson
import gridfs

from concurrent.futures import ThreadPoolExecutor
import multiprocessing
from typing import List

import cy_kit
from cyx.base import BaseService
class FilesSync(BaseService):
    def __init__(self):
        self.msg_service=msg_service
        self.db = db
        self.clean_up = clean_up
        self.working_dir = pathlib.Path(__file__).parent.parent.__str__()
        self.file_dir = os.path.join(self.working_dir, "background_service_files", "file")
        self.logs_dir = os.path.join(self.working_dir, "background_service_files", "logs")
        if not os.path.isdir(self.file_dir):
            os.makedirs(self.file_dir, exist_ok=True)
        if not os.path.isdir(self.logs_dir):
            os.makedirs(self.logs_dir, exist_ok=True)
        self.logs = loggers.get_logger(SyncToLocalService.__name__, self.logs_dir)
        self.logs.info(
            f"start service {SyncToLocalService.__name__}"
        )

    def sync_file(self, item: enig_frames.services.msgs.MessageInfo):
        upload_id = item.Data.get("_id")
        upload_item = item.Data
        app_db = self.db.context(item.AppName)
        if not upload_item:
            return
        file_ext = upload_item[api_models.documents.Files.FileExt.__name__]
        full_file_path = os.path.join(self.file_dir, f"{upload_id}.{file_ext}")
        if os.path.isfile(full_file_path):
            return full_file_path
        file_id = upload_item[api_models.documents.Files.MainFileId.__name__]

        current_chunk_index = 0
        num_of_chunks = upload_item[api_models.documents.MediaTracking.NumOfChunks.__name__]

        start_time = datetime.datetime.utcnow()

        self.logs.info(f"start sync file {full_file_path} at {datetime.datetime.utcnow()}")

        try:
            timeout_count = 0
            _file_id = file_id
            if isinstance(file_id,str):
                _file_id = bson.ObjectId(file_id)

            while current_chunk_index < num_of_chunks:

                chunk = app_db.find_one(
                    api_models.documents.FsChunks,
                    filter={
                        "files_id": _file_id,
                        "n": current_chunk_index
                    }
                )
                if timeout_count > 100:
                    self.logs.info(f"sync file {full_file_path} fail, timeout {timeout_count / 2} senconds")
                    os.remove(full_file_path)

                    return
                if chunk is None:
                    time.sleep(0.5)
                    timeout_count += 1

                else:
                    if not os.path.isfile(full_file_path):
                        with open(full_file_path, "wb") as f:
                            f.write(chunk["data"])
                        del chunk["data"]
                        self.clean_up.clean_up()
                    else:
                        with open(full_file_path, "ab") as f:
                            f.write(chunk["data"])
                        del chunk["data"]
                        self.clean_up.clean_up()
                    current_chunk_index += 1
                time.sleep(0.001)
            total_seconds = (datetime.datetime.utcnow() - start_time).total_seconds()
            self.logs.info(f"sync file {full_file_path} complete in {total_seconds} second")


            return full_file_path

        except Exception as e:
            self.logs.exception(e)

        finally:
            self.clean_up.clean_up()
    def sync_file_in_thread(self,item:enig_frames.services.msgs.MessageInfo,plugins,output:dict):
        def run(_output:dict):
            _output={}
            try:
                full_file_path = self.sync_file(item)
                if full_file_path is None:

                    return
                app_name = item.AppName
                upload_id = item.Data["_id"]
                list_of_plugin_threads:List[threading.Thread] =[]
                for x in plugins:
                    def run(call,full_file_path, app_name, upload_id):
                        try:
                            if callable(call):
                                print(f"{call.__module__}/{call.__name__}\n")
                                call(full_file_path,app_name,upload_id)
                                print(f"file { full_file_path}\n")
                        except Exception as e:
                            print(f"file fail {full_file_path}\n")
                            os.remove(full_file_path)
                            self.msg_service.delete(item)
                    list_of_plugin_threads+=[threading.Thread(target=run,args=(x,full_file_path, app_name, upload_id,))]
                # with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()-1) as executor:
                #     ordinal = 1
                #     for x in plugins:
                #         executor.submit(x, (full_file_path, app_name, upload_id))
                for t in list_of_plugin_threads:
                    t.start()
                for t in list_of_plugin_threads:
                    t.join()
                os.remove(full_file_path)
                self.msg_service.delete(item)
                self.clean_up.clean_up()
            except Exception as e:

                self.logs.exception(e)
                _output['error']=e


        th_run = threading.Thread(target=run,args=(output,)).start()
        return th_run