import threading
import time

import api_models.documents
import enig
import enig_frames.containers
import enig_frames.services.msgs
import enig_frames.config
container = enig_frames.containers.Container
import sync_local_files
import process_contents
sync_local_service = enig.depen(sync_local_files.SyncToLocalService)
process_contents_service = enig.depen(process_contents.ProcessContents)
message_service = enig.depen(
    enig_frames.services.msgs.Message
)
config = enig.depen(
    enig_frames.config.Configuration
)
import enig_frames.plugins.thumbs.office
import enig_frames.plugins.thumbs.pdf
import enig_frames.plugins.thumbs.images
import enig_frames.plugins.thumbs.video
import enig_frames.plugins.thumbs.exe_file
import enig_frames.plugins.ocr.images
import enig_frames.plugins.ocr.pdf_file
import enig_frames.plugins.search.office

plug_in_list =[
    enig.depen(enig_frames.plugins.thumbs.office.Office).process,
    enig.depen(enig_frames.plugins.thumbs.pdf.PDF).process,
    enig.depen(enig_frames.plugins.thumbs.images.Images).process,
    enig.depen(enig_frames.plugins.thumbs.video.Video).process,
    enig.depen(enig_frames.plugins.thumbs.exe_file.ExeFile).process,
    enig.depen(enig_frames.plugins.ocr.images.Images).process,
    enig.depen(enig_frames.plugins.ocr.pdf_file.PdfFile).process,
    enig.depen(enig_frames.plugins.search.office.Office).process,


]
def run():
    while True:
        items = message_service.get_message(
            message_type='files.upload'
        )
        for x in items:
            upload_item = x.Data
            app_name = x.AppName
            file_ext = upload_item[api_models.documents.Files.FileExt.__name__]
            mime_type = upload_item[api_models.documents.Files.MimeType.__name__]
            full_file_path = sync_local_service.sync_file_in_thread(
                item=x,
                plugins=plug_in_list)
            print(f"{upload_item['_id']}.{file_ext}")


        time.sleep(0.2)