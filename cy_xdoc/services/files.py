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
            doc.SizeInBytes >> cy_docs.fields.FileSize,
            doc.Id >> cy_docs.fields.UploadID,
            doc.RegisterOn >> cy_docs.fields.CreatedOn,
            doc.FileNameOnly,
            cy_docs.concat(root_url, f"/api/{app_name}/file/", doc.FullFileName) >> cy_docs.fields.UrlOfServerPath,
            cy_docs.concat(f"api/{app_name}/file/", doc.FullFileName) >> cy_docs.fields.RelUrlOfServerPath,
            cy_docs.concat(root_url, f"/api/{app_name}/thumb/", doc.FullFileName, ".webp") >> cy_docs.fields.ThumbUrl,
            doc.AvailableThumbs
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
        file_id = upload.MainFileId
        fs = self.get_file(app_name, file_id)
        return fs

    async def get_main_file_of_upload_async(self, app_name, upload_id):
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        if not upload:
            return

        file_id = upload.MainFileId
        if file_id is not None:
            fs = await self.get_file_async(app_name, file_id)

        return fs

    def find_file_async(self, app_name, relative_file_path):
        pass
