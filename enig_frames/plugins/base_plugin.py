import enig
import api_models.documents
import enig_frames.services.file_system
import enig_frames.services.files

class BasePlugin(enig.Singleton):
    def process(self, file_path: str, app_name: str, upload_id: str):
        raise NotImplemented

    def make_available_thumbs(self,
                              app_name: str,
                              image_file: str,
                              upload_id: str,
                              file_system_services: enig_frames.services.file_system.FileSystem,
                              file_services: enig_frames.services.files.Files
                              ):
        upload = file_services.get_item_by_upload_id(
            app_name=app_name,
            upload_id=upload_id
        )
        available_thumb_size = upload[api_models.documents.Files.AvailableThumbSize]
        if available_thumb_size is not None:
            sizes = available_thumb_size.split(',')
            for size in sizes:
                if isinstance(size, str) and size.isnumeric():
                    i_size = int(size)
                    dynamic_thumb_file = self.image_service.create_thumbs(image_file, i_size)
                    rel_thumb_url = f"thumbs/{upload_id}/{size}.webp"
                    file_system_services.upload(
                        app_name=app_name,
                        full_path_to_file=dynamic_thumb_file,
                        rel_file_path=rel_thumb_url

                    )
                    upload = file_services.get_item_by_upload_id(
                        app_name=app_name,
                        upload_id=upload_id
                    )
                    available_thumbs = upload[api_models.documents.Files.AvailableThumbs]
                    if available_thumbs is None:
                        available_thumbs = [rel_thumb_url]
                    else:
                        available_thumbs+=[rel_thumb_url]
                    file_services.update_file_field(
                        app_name=app_name,
                        upload_id=upload_id,
                        field = api_models.documents.Files.AvailableThumbs,
                        value= available_thumbs

                    )

