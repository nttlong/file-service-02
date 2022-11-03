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
            full_file_path = sync_local_service.sync_file(x)
            if file_ext in config.config.ext_office_file:
                message_service.emit(
                    app_name= app_name,
                    message_type= 'files.office.thumbs',
                    data= dict(
                        upload_item = upload_item,
                        file_path = full_file_path
                    )
                )
                message_service.emit(
                    app_name=app_name,
                    message_type='files.office.search',
                    data=dict(
                        upload_item=upload_item,
                        file_path=full_file_path
                    )
                )
                message_service.delete(x)
        time.sleep(0.2)