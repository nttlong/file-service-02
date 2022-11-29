import threading
import time

from cyx.common.msg import MessageService
import cy_kit
import cyx.common
message_service:MessageService = cy_kit.singleton(
    MessageService
)
config = cyx.common.config
# import enig_frames.plugins.thumbs.office
# import enig_frames.plugins.thumbs.pdf
# import enig_frames.plugins.thumbs.images
# import enig_frames.plugins.thumbs.video
# import enig_frames.plugins.thumbs.exe_file
# import enig_frames.plugins.ocr.images
# import enig_frames.plugins.ocr.pdf_file
# import enig_frames.plugins.search.office

plug_in_list_delete =[
    # enig.depen(enig_frames.plugins.thumbs.office.Office).process,
    # enig.depen(enig_frames.plugins.thumbs.pdf.PDF).process,
    # enig.depen(enig_frames.plugins.thumbs.images.Images).process,
    # enig.depen(enig_frames.plugins.thumbs.video.Video).process,
    # enig.depen(enig_frames.plugins.thumbs.exe_file.ExeFile).process,
    # enig.depen(enig_frames.plugins.ocr.images.Images).process,
    # enig.depen(enig_frames.plugins.ocr.pdf_file.PdfFile).process,
    # enig.depen(enig_frames.plugins.search.office.Office).process,


]
plug_in_list=[]
import multiprocessing
import concurrent.futures
from cyx.file_sync import FilesSync
file_sync_service = cy_kit.singleton(FilesSync)
def run():
    while True:
        items = message_service.get_message(
            message_type='files.upload'
        )
        output={}
        def run(x):
            if message_service.is_lock(x):
                return
            message_service.lock(x)
            try:
                upload_item = x.Data
                app_name = x.AppName
                file_ext = upload_item.FileExt

                mime_type = upload_item.MimeType
                full_file_path = file_sync_service.sync_file_in_thread(
                    item=x,
                    plugins=plug_in_list, output=output)
                print(f"{upload_item['_id']}.{file_ext}")
                print(output)
            except Exception as e:
                print(e)
                message_service.unlock(x)
            finally:
                message_service.delete(x)
        workers_numbers=max(multiprocessing.cpu_count() - 1,2)*10
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers_numbers) as executor:

            for x in items:
                executor.submit(run,x)


        time.sleep(0.05)