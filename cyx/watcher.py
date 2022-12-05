import os
import pathlib
import threading
import time

import cy_docs
from cyx.common.msg import MessageService, MessageInfo
import cy_kit
import cyx.common
import multiprocessing
import concurrent.futures
from cyx.file_sync import FilesSync
from cyx.media.image_extractor import ImageExtractorService
from cyx.file_content_process import FileContentProcessService
from cy_xdoc.services.files import FileServices
message_service: MessageService = cy_kit.singleton(
    MessageService
)
config = cyx.common.config
file_content_process_service = cy_kit.singleton(FileContentProcessService)

file_sync_service = cy_kit.singleton(FilesSync)
file_services = cy_kit.singleton(FileServices)

message_type = 'files.upload'





watcher_log = cy_kit.create_logs(
    log_dir=os.path.join(pathlib.Path(__file__).parent.parent.__str__(), "background_service_files", "logs"),
    name=pathlib.Path(__file__).stem
)


def run(use_thread=True):
    try:
        message_service.reset_status(message_type)
        while True:
            try:
                items = message_service.get_message(
                    message_type='files.upload'
                )
                output = {}

                def run(x:MessageInfo):
                    print("---new msg ------")
                    print(x)
                    if message_service.is_lock(x):
                        return
                    message_service.lock(x)
                    try:
                        upload_item = cy_docs.DocumentObject(x.Data)
                        real_upload = file_services.get_upload_register(
                            app_name= x.AppName,
                            upload_id= x.Data.get("_id")
                        )
                        if not real_upload:
                            message_service.delete(x)
                            return
                        app_name = x.AppName
                        file_ext = upload_item.FileExt

                        mime_type = upload_item.MimeType
                        full_file_path = file_sync_service.sync_file_in_thread(
                            item=x,

                            output=output,
                            use_thread=use_thread,
                            handler_service= file_content_process_service,

                        )
                        message_service.delete(x)
                        os.remove(full_file_path)

                    except Exception as e:
                        watcher_log.exception(e)

                if use_thread:
                    workers_numbers = max(multiprocessing.cpu_count() - 1, 2) * 10
                    with concurrent.futures.ThreadPoolExecutor(max_workers=workers_numbers) as executor:

                        for x in items:
                            executor.submit(run, x)
                else:
                    for x in items:
                        run(x)
                time.sleep(0.05)
            except Exception as e:
                watcher_log.exception(e)
    except Exception as e:
        watcher_log.exception(e)
        watcher_log.info("Can not start")
