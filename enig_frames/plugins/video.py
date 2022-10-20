import api_models.documents
import enig
import enig_frames.config
import enig_frames.services.videos
import enig_frames.services.images
import enig_frames.plugins.base_plugin
import enig_frames.services.file_system
import enig_frames.services.files



class PlugInVideo(enig_frames.plugins.base_plugin.BasePlugin):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 ),
                 video_services: enig_frames.services.videos.VideoService = enig.depen(
                     enig_frames.services.videos.VideoService
                 ),
                 image_service: enig_frames.services.images.ImageServices = enig.depen(
                     enig_frames.services.images.ImageServices
                 ),
                 file_system_services: enig_frames.services.file_system.FileSystem = enig.depen(
                     enig_frames.services.file_system.FileSystem
                 ),
                 file_services: enig_frames.services.files.Files = enig.depen(
                     enig_frames.services.files.Files
                 ),
                 file_system_utils:enig_frames.services.file_system_utils.FileSystemUtils=enig.depen(
                     enig_frames.services.file_system_utils.FileSystemUtils
                 )):
        enig_frames.plugins.base_plugin.BasePlugin.__init__(self)
        self.configuration: enig_frames.config.Configuration = configuration
        self.video_services: enig_frames.services.videos.VideoService = video_services
        self.image_service:enig_frames.services.images.ImageServices = image_service
        self.file_system_services: enig_frames.services.file_system.FileSystem = file_system_services
        self.file_services: enig_frames.services.files.Files = file_services
        self.file_system_utils:enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils

    def process(self, file_path: str, app_name: str, upload_id: str):
        m_type:str = self.file_system_utils.get_mime_type(file_path)
        if m_type.startswith('video/'):
            image_file: str = self.video_services.get_image_from_frame(
                file_path=file_path
            )
            thumb_file = self.image_service.create_thumbs(image_file,450)
            file_name_only = self.file_system_utils.get_file_name_only(file_path)
            file_ext_only = self.file_system_utils.get_file_extenstion(thumb_file)
            file_info = self.file_system_services.upload(
                app_name=app_name,
                full_path_to_file=thumb_file

            )
            rel_file_path = f"thumb/{upload_id}/{file_name_only}.{file_ext_only}"
            self.file_services.update_rel_path(
                app_name = app_name,
                file_id = str(file_info._id),
                rel_file_path =rel_file_path)
            self.file_services.update_file_field(
                app_name=app_name,
                upload_id=upload_id,
                field = api_models.documents.Files.HasThumb,
                value = True

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
                image_file=image_file,
                file_system_services=self.file_system_services,
                file_services=self.file_services

            )








