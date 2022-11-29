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
        mime_type, _ = mimetypes.guess_type(full_file_path)
        if mime_type.startswith("image/"):
            pdf_file_path = self.image_extractor_service.convert_to_pdf(file_path=full_file_path)
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

            if doc_data.AvailableThumbSize:
                sizes = [ int(x) for  x in doc_data.AvailableThumbSize.split(',') if x.strip().isnumeric()]
                available_thumbs =[]
                for x in sizes:
                    self.create_thumbs(
                        app_name = msg.AppName,
                        upload_id = doc_data.id,
                        image_source_path = image_file_path,
                        scale_to_size = x

                    )
                    available_thumbs += [f"thumbs/{doc_data.id}/{x}.webp"]

                self.file_services.update_available_thumbs(
                    upload_id=doc_data.id,
                    app_name = msg.AppName,
                    available_thumbs = available_thumbs

                )







    def create_thumbs(self, app_name:str, upload_id:str, image_source_path:str, scale_to_size: int):

        thumb_path = self.image_extractor_service.create_thumb(image_source_path, size=scale_to_size)
        self.file_storage_services.store_file(
            app_name= app_name,
            source_file=thumb_path,
            rel_file_store_path=f"thumbs/{upload_id}/{scale_to_size}.webp",
        )

