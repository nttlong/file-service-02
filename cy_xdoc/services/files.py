import datetime
import uuid

import cy_docs
from cy_xdoc.services.base import Base
from cy_xdoc.models.files import DocUploadRegister


class FileServices(Base):
    def __init__(self):
        Base.__init__(self)

    def get_list(self, app_name, root_url, page_index: int, page_size: int, field_search: str = None,
                 value_search: str = None):
        doc = self.expr(DocUploadRegister)
        items = self.db(app_name).doc(DocUploadRegister).aggregate().sort(
            doc.RegisterOn.desc(),
            doc.Status.desc()
        ).skip(page_size * page_index).limit(page_size).project(
            doc.FileName,
            doc.Status,
            doc.SizeInHumanReadable,
            doc.ServerFileName,
            doc.IsPublic,
            doc.FullFileName,
            doc.MimeType,
            cy_docs.fields.FileSize >> doc.SizeInBytes,
            cy_docs.fields.UploadID>>doc.Id  ,
            cy_docs.fields.CreatedOn>>doc.RegisterOn  ,
            doc.FileNameOnly,
            cy_docs.fields.UrlOfServerPath >> cy_docs.concat(root_url, f"/api/{app_name}/file/", doc.FullFileName),
            cy_docs.fields.RelUrlOfServerPath>>cy_docs.concat(f"api/{app_name}/file/", doc.FullFileName) ,
            cy_docs.fields.ThumbUrl>>cy_docs.concat(root_url, f"/api/{app_name}/thumb/", doc.FullFileName, ".webp") ,
            doc.AvailableThumbs,
            doc.HasThumb,
            doc.OCRFileId,
            cy_docs.fields.Media>>(
                cy_docs.fields.Width>>doc.VideoResolutionWidth,
                cy_docs.fields.Height >> doc.VideoResolutionHeight,
                cy_docs.fields.Duration>>doc.VideoDuration,
                cy_docs.fields.FPS >> doc.VideoFPS
            )

        )
        for x in items:
            _a_thumbs = []
            if x.AvailableThumbs is not None:
                for url in x.AvailableThumbs:
                    _a_thumbs += [f"api/{app_name}/thumbs/{url}"]
                x["AvailableThumbs"] = _a_thumbs
            yield x

    def get_main_file_of_upload(self, app_name, upload_id):
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        if not upload:
            return
        if upload.MainFileId is None:
            return None
        fs = self.get_file(app_name, upload.MainFileId)
        return fs

    async def get_main_file_of_upload_async(self, app_name, upload_id):
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        if not upload:
            return


        if upload.MainFileId is not None:
            fs = await self.get_file_async(app_name, upload.MainFileId)
            return fs
        else:
            return None

    def find_file_async(self, app_name, relative_file_path):
        pass


    def get_main_main_thumb_file(self, app_name, upload_id):
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        if upload is None:
            return None
        ret = self.get_file(app_name,upload.ThumbFileId)
        return ret
