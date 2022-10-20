import enig
import enig_frames.plugins.base_plugin
import enig_frames.config
import api_models.documents
import enig_frames.services.file_system_utils
import enig_frames.services.PDFs
import enig_frames.services.images
import enig_frames.services.file_system
import enig_frames.services.files
class Images(enig_frames.plugins.base_plugin.BasePlugin):
    def __init__(
            self,
            configuration: enig_frames.config.Configuration = enig.depen(
                enig_frames.config.Configuration
            ),
            file_system_utils: enig_frames.services.file_system_utils = enig.depen(
                enig_frames.services.file_system_utils.FileSystemUtils
            ),
            pdf_file_service: enig_frames.services.PDFs.PdfFileService = enig.depen(
                enig_frames.services.PDFs.PdfFileService
            ),
            image_service:enig_frames.services.images.ImageServices = enig.depen(
                enig_frames.services.images.ImageServices
            ),
            file_system_services: enig_frames.services.file_system.FileSystem = enig.depen(
                enig_frames.services.file_system.FileSystem
            ),
            file_services: enig_frames.services.files.Files = enig.depen(
                enig_frames.services.files.Files
            )
    ):
        self.configuration: enig_frames.config.Configuration = configuration
        self.file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils
        self.pdf_file_service: enig_frames.services.PDFs.PdfFileService = pdf_file_service
        self.image_service:enig_frames.services.images.ImageServices = image_service
        self.file_system_services:enig_frames.services.file_system.FileSystem = file_system_services
        self.file_services:enig_frames.services.files.Files= file_services
        enig_frames.plugins.base_plugin.BasePlugin.__init__(self)

    def process(self, file_path: str, app_name: str, upload_id: str):
        mime_type = self.file_system_utils.get_mime_type(file_path)
        if mime_type.lower().startswith("image/"):
            file_ext_only = self.file_system_utils.get_file_extenstion(file_path)
            thumb_file = self.image_service.create_thumbs(file_path, 450)

            file_name_only = self.file_system_utils.get_file_name_only(thumb_file)
            file_info = self.file_system_services.upload(
                app_name=app_name,
                full_path_to_file=thumb_file

            )
            rel_file_path = f"thumb/{upload_id}/{file_name_only}.{file_ext_only}"
            self.file_services.update_rel_path(
                app_name=app_name,
                file_id=str(file_info._id),
                rel_file_path=rel_file_path)
            self.file_services.update_file_field(
                app_name=app_name,
                upload_id=upload_id,
                field=api_models.documents.Files.HasThumb,
                value=True

            )
            self.file_services.update_file_field(
                app_name=app_name,
                upload_id=upload_id,
                field=api_models.documents.Files.ThumbFileId,
                value=file_info._id

            )
            self.make_available_thumbs(
                upload_id=upload_id,
                app_name=app_name,
                image_file=file_path,
                file_system_services=self.file_system_services,
                file_services=self.file_services

            )
