import datetime
import mimetypes
import os.path
import pathlib
import uuid
import humanize
import cy_docs
import cy_kit
from cy_xdoc.services.base import Base
from cy_xdoc.models.files import DocUploadRegister
import cy_xdoc.services.file_storage
import cy_xdoc.services.search_engine

class FileServices(Base):
    def __init__(self,
                 file_storage_service=cy_kit.provider(cy_xdoc.services.file_storage.FileStorageService),
                 search_engine = cy_kit.single(cy_xdoc.services.search_engine.SearchEngine)):

        self.file_storage_service = file_storage_service
        self.search_engine = search_engine

    def get_list(self, app_name, root_url, page_index: int, page_size: int, field_search: str = None,
                 value_search: str = None):

        doc = self.expr(DocUploadRegister)
        arrg = self.db(app_name).doc(DocUploadRegister).aggregate()
        if value_search is not None and value_search!="":
            if field_search is None or field_search=="":
                field_search="FileName"
            import re
            arrg=arrg.match(getattr(doc,field_search).like(value_search))
        items = arrg.sort(
            doc.RegisterOn.desc(),
            doc.Status.desc()
        ).skip(page_size * page_index).limit(page_size).project(
            cy_docs.fields.UploadId>>doc.id,
            doc.FileName,
            doc.Status,
            doc.SizeInHumanReadable,
            doc.ServerFileName,
            doc.IsPublic,
            doc.FullFileName,
            doc.MimeType,
            cy_docs.fields.FileSize >> doc.SizeInBytes,
            cy_docs.fields.UploadID >> doc.Id,
            cy_docs.fields.CreatedOn >> doc.RegisterOn,
            doc.FileNameOnly,
            cy_docs.fields.UrlOfServerPath >> cy_docs.concat(root_url, f"/api/{app_name}/file/", doc.FullFileName),
            cy_docs.fields.RelUrlOfServerPath >> cy_docs.concat(f"api/{app_name}/file/", doc.FullFileName),
            cy_docs.fields.ThumbUrl >> cy_docs.concat(root_url, f"/api/{app_name}/thumb/", doc.FullFileName, ".webp"),
            doc.AvailableThumbs,
            doc.HasThumb,
            doc.OCRFileId,
            cy_docs.fields.Media >> (
                cy_docs.fields.Width >> doc.VideoResolutionWidth,
                cy_docs.fields.Height >> doc.VideoResolutionHeight,
                cy_docs.fields.Duration >> doc.VideoDuration,
                cy_docs.fields.FPS >> doc.VideoFPS
            )


        )
        for x in items:
            _a_thumbs = []
            if x.AvailableThumbs is not None:
                for url in x.AvailableThumbs:
                    _a_thumbs += [f"api/{app_name}/thumbs/{url}"]
                x["AvailableThumbs"] = _a_thumbs
            if x.OCRFileId:
                x["OcrContentUrl"]=f"{root_url}/api/{app_name}/file-ocr/{x.FileNameOnly.lower()}.pdf"
            yield x

    def get_main_file_of_upload(self, app_name, upload_id):
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        if not upload:
            return
        if upload.MainFileId is None:
            return None
        fs = self.file_storage_service.instance.get_file_by_id(
            app_name=app_name,
            id= str(upload.MainFileId)
        )
        # self.get_file(app_name, upload.MainFileId)
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
        ret = self.file_storage_service.instance.get_file_by_id(app_name=app_name,id=upload.ThumbFileId)
            # self.get_file(app_name, upload.ThumbFileId)
        return ret

    def add_new_upload_info(self,
                            app_name,
                            client_file_name: str,
                            is_public: bool,
                            file_size: int,
                            chunk_size: int,
                            thumbs_support: str,
                            web_host_root_url: str):

        doc = self.expr(DocUploadRegister)
        id = str(uuid.uuid4())
        mime_type, _ = mimetypes.guess_type(client_file_name)
        num_of_chunks, tail = divmod(file_size, chunk_size)
        if tail > 0:
            num_of_chunks += 1
        ret = self.db(app_name).doc(DocUploadRegister).insert_one(
            doc.id << id,
            doc.FileName << client_file_name,
            doc.FileNameOnly << pathlib.Path(client_file_name).stem,
            doc.FileNameLower << client_file_name.lower(),
            doc.FileExt << os.path.splitext(client_file_name)[1].split('.')[1],
            doc.FullFileName << f"{id}/{client_file_name}",
            doc.FullFileNameLower << f"{id}/{client_file_name}".lower(),
            doc.FullFileNameWithoutExtenstion << f"{id}/{pathlib.Path(client_file_name).stem}",
            doc.FullFileNameWithoutExtenstionLower << f"{id}/{pathlib.Path(client_file_name).stem}".lower(),
            doc.ServerFileName << f"{id}.{os.path.splitext(client_file_name)[1].split('.')[1]}",
            doc.AvailableThumbSize << thumbs_support,

            doc.ChunkSizeInKB << chunk_size / 1024,
            doc.ChunkSizeInBytes << chunk_size,
            doc.NumOfChunks << num_of_chunks,
            doc.NumOfChunksCompleted << 0,
            doc.SizeInHumanReadable << humanize.filesize.naturalsize(file_size),
            doc.SizeUploaded << 0,
            doc.ProcessHistories << [],
            doc.MimeType << mime_type,
            doc.IsPublic << is_public,
            doc.Status << 0,
            doc.RegisterOn << datetime.datetime.utcnow(),
            doc.RegisterOnDays << datetime.datetime.utcnow().day,
            doc.RegisterOnMonths << datetime.datetime.utcnow().month,
            doc.RegisterOnYears << datetime.datetime.utcnow().year,
            doc.RegisterOnHours << datetime.datetime.utcnow().hour,
            doc.RegisterOnMinutes << datetime.datetime.utcnow().minute,
            doc.RegisterOnSeconds << datetime.datetime.utcnow().second,
            doc.RegisteredBy << app_name,
            doc.HasThumb << False,
            doc.LastModifiedOn << datetime.datetime.utcnow(),
            doc.SizeInBytes << file_size
        )
        return cy_docs.DocumentObject(
            NumOfChunks=num_of_chunks,
            ChunkSizeInBytes=chunk_size,
            UploadId=id,
            ServerFilePath=f"{id}{os.path.splitext(client_file_name)[1]}",
            MimeType=mime_type,
            RelUrlOfServerPath=f"api/{app_name}/file/register/{id}/{pathlib.Path(client_file_name).stem.lower()}",
            SizeInHumanReadable=humanize.filesize.naturalsize(file_size),
            UrlOfServerPath=f"{web_host_root_url}/api/{app_name}/file/register/{id}/{pathlib.Path(client_file_name).stem.lower()}",
            RelUrlThumb=f"api/{app_name}/thumb/{id}/{pathlib.Path(client_file_name).stem.lower()}.webp",
            FileSize=file_size,
            UrlThumb=f"{web_host_root_url}/api/{app_name}/thumb/{id}/{pathlib.Path(client_file_name).stem.lower()}.webp",
            OriginalFileName=client_file_name
        )

    def get_upload_register(self, app_name: str, UploadId: str):
        return self.db(app_name).doc(DocUploadRegister) @ UploadId


    def remove_upload(self, app_name, upload_id):
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        delete_file_list = upload.AvailableThumbs or []
        delete_file_list_by_id =[]
        if upload.MainFileId is not None: delete_file_list_by_id = [str(upload.MainFileId)]
        if upload.OCRFileId is not None: delete_file_list_by_id+=[str(upload.OCRFileId)]
        if upload.ThumbFileId is not None: delete_file_list_by_id += [str(upload.ThumbFileId)]
        self.file_storage_service.instance.delete_files(app_name=app_name,files = delete_file_list,run_in_thread=True)
        self.file_storage_service.instance.delete_files_by_id(app_name=app_name,ids =delete_file_list_by_id, run_in_thread=True)
        self.search_engine.delete_doc(app_name,upload_id)
        ret = self.db(app_name).doc(DocUploadRegister).delete(cy_docs.fields._id==upload_id)
        return





        pass
