import os

import cy_docs

from cyx.common.msg import MessageService, MessageInfo
from cyx.media.image_extractor import ImageExtractorService
from cyx.common.file_storage_mongodb import MongoDbFileStorage, MongoDbFileService
from cy_xdoc.services.files import FileServices
import cy_web
import mimetypes
import cy_kit


class FileContentProcessService:
    def __init__(
            self,
            image_extractor_service: ImageExtractorService = cy_kit.singleton(ImageExtractorService),
            file_storage_services: MongoDbFileService = cy_kit.singleton(MongoDbFileService),
            file_services: FileServices = cy_kit.singleton(FileServices)

    ):
        self.image_extractor_service = image_extractor_service
        self.file_storage_services: MongoDbFileService = file_storage_services
        self.file_services: FileServices = file_services

    def resolve(self, msg: MessageInfo, full_file_path: str):
        doc_data = cy_docs.DocumentObject(msg.Data)
        if full_file_path is None:
            return
        image_file_path = self.image_extractor_service.get_image(file_path=full_file_path)
        if image_file_path is not None:
            main_thumb_path = self.image_extractor_service.create_thumb(image_file_path, size=500)
            content_type,_ = mimetypes.guess_type(main_thumb_path)
            fs = self.file_storage_services.store_file(
                app_name=msg.AppName,
                source_file = main_thumb_path,
                rel_file_store_path=f"thumb/{doc_data.FullFileNameLower}.webp",
            )

            self.file_services.update_main_thumb_id(
                app_name = msg.AppName,
                upload_id =  doc_data.id,
                main_thumb_id = fs.get_id()

            )



            print(main_thumb_path)
