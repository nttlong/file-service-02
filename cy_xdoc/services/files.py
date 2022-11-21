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

class FileServices:
    def __init__(self,
                 file_storage_service=cy_kit.inject(cy_xdoc.services.file_storage.FileStorageService),
                 search_engine = cy_kit.inject(cy_xdoc.services.search_engine.SearchEngine),
                 db_connect = cy_kit.inject(cy_xdoc.services.base.DbConnect)):

        self.file_storage_service = file_storage_service
        self.search_engine = search_engine
        self.db_connect= db_connect

    def get_list(self, app_name, root_url, page_index: int, page_size: int, field_search: str = None,
                 value_search: str = None):

        doc = self.db_connect.db(app_name).doc(DocUploadRegister)
        arrg = doc.context.aggregate()
        if value_search is not None and value_search!="":
            if field_search is None or field_search=="":
                field_search="FileName"
            import re
            arrg=arrg.match(getattr(doc.fields,field_search).like(value_search))
        items = arrg.sort(
            doc.fields.RegisterOn.desc(),
            doc.fields.Status.desc()
        ).skip(page_size * page_index).limit(page_size).project(
            cy_docs.fields.UploadId>>doc.fields.id,
            doc.fields.FileName,
            doc.fields.Status,
            doc.fields.SizeInHumanReadable,
            doc.fields.ServerFileName,
            doc.fields.IsPublic,
            doc.fields.FullFileName,
            doc.fields.MimeType,
            cy_docs.fields.FileSize >> doc.fields.SizeInBytes,
            cy_docs.fields.UploadID >> doc.fields.Id,
            cy_docs.fields.CreatedOn >> doc.fields.RegisterOn,
            doc.fields.FileNameOnly,
            cy_docs.fields.UrlOfServerPath >> cy_docs.concat(root_url, f"/api/{app_name}/file/", doc.fields.FullFileName),
            cy_docs.fields.RelUrlOfServerPath >> cy_docs.concat(f"api/{app_name}/file/", doc.fields.FullFileName),
            cy_docs.fields.ThumbUrl >> cy_docs.concat(root_url, f"/api/{app_name}/thumb/", doc.fields.FullFileName, ".webp"),
            doc.fields.AvailableThumbs,
            doc.fields.HasThumb,
            doc.fields.OCRFileId,
            cy_docs.fields.Media >> (
                cy_docs.fields.Width >> doc.fields.VideoResolutionWidth,
                cy_docs.fields.Height >> doc.fields.VideoResolutionHeight,
                cy_docs.fields.Duration >> doc.fields.VideoDuration,
                cy_docs.fields.FPS >> doc.fields.VideoFPS
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
        upload = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
        if not upload:
            return
        if upload.MainFileId is None:
            return None
        fs = self.file_storage_service.get_file_by_id(
            app_name=app_name,
            id= str(upload.MainFileId)
        )
        # self.get_file(app_name, upload.MainFileId)
        return fs

    async def get_main_file_of_upload_async(self, app_name, upload_id):
        upload = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
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
        upload = self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id
        if upload is None:
            return None
        ret = self.file_storage_service.get_file_by_id(app_name=app_name,id=upload.ThumbFileId)
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

        doc = self.db_connect.db(app_name).doc(DocUploadRegister)
        id = str(uuid.uuid4())
        mime_type, _ = mimetypes.guess_type(client_file_name)
        num_of_chunks, tail = divmod(file_size, chunk_size)
        if tail > 0:
            num_of_chunks += 1
        ret = doc.context.insert_one(
            doc.fields.id << id,
            doc.fields.FileName << client_file_name,
            doc.fields.FileNameOnly << pathlib.Path(client_file_name).stem,
            doc.fields.FileNameLower << client_file_name.lower(),
            doc.fields.FileExt << os.path.splitext(client_file_name)[1].split('.')[1],
            doc.fields.FullFileName << f"{id}/{client_file_name}",
            doc.fields.FullFileNameLower << f"{id}/{client_file_name}".lower(),
            doc.fields.FullFileNameWithoutExtenstion << f"{id}/{pathlib.Path(client_file_name).stem}",
            doc.fields.FullFileNameWithoutExtenstionLower << f"{id}/{pathlib.Path(client_file_name).stem}".lower(),
            doc.fields.ServerFileName << f"{id}.{os.path.splitext(client_file_name)[1].split('.')[1]}",
            doc.fields.AvailableThumbSize << thumbs_support,

            doc.fields.ChunkSizeInKB << chunk_size / 1024,
            doc.fields.ChunkSizeInBytes << chunk_size,
            doc.fields.NumOfChunks << num_of_chunks,
            doc.fields.NumOfChunksCompleted << 0,
            doc.fields.SizeInHumanReadable << humanize.filesize.naturalsize(file_size),
            doc.fields.SizeUploaded << 0,
            doc.fields.ProcessHistories << [],
            doc.fields.MimeType << mime_type,
            doc.fields.IsPublic << is_public,
            doc.fields.Status << 0,
            doc.fields.RegisterOn << datetime.datetime.utcnow(),
            doc.fields.RegisterOnDays << datetime.datetime.utcnow().day,
            doc.fields.RegisterOnMonths << datetime.datetime.utcnow().month,
            doc.fields.RegisterOnYears << datetime.datetime.utcnow().year,
            doc.fields.RegisterOnHours << datetime.datetime.utcnow().hour,
            doc.fields.RegisterOnMinutes << datetime.datetime.utcnow().minute,
            doc.fields.RegisterOnSeconds << datetime.datetime.utcnow().second,
            doc.fields.RegisteredBy << app_name,
            doc.fields.HasThumb << False,
            doc.fields.LastModifiedOn << datetime.datetime.utcnow(),
            doc.fields.SizeInBytes << file_size
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

    def get_upload_register(self, app_name: str, upload_id: str):
        return self.db_connect.db(app_name).doc(DocUploadRegister).context @ upload_id


    def remove_upload(self, app_name, upload_id):
        upload = self.db_connect.db(app_name).doc(DocUploadRegister).context  @ upload_id
        delete_file_list = upload.AvailableThumbs or []
        delete_file_list_by_id =[]
        if upload.MainFileId is not None: delete_file_list_by_id = [str(upload.MainFileId)]
        if upload.OCRFileId is not None: delete_file_list_by_id+=[str(upload.OCRFileId)]
        if upload.ThumbFileId is not None: delete_file_list_by_id += [str(upload.ThumbFileId)]
        self.file_storage_service.delete_files(app_name=app_name,files = delete_file_list,run_in_thread=True)
        self.file_storage_service.delete_files_by_id(app_name=app_name,ids =delete_file_list_by_id, run_in_thread=True)
        self.search_engine.delete_doc(app_name,upload_id)
        doc= self.db_connect.db(app_name).doc(DocUploadRegister)
        ret = doc.context.delete(cy_docs.fields._id==upload_id)
        return





        pass
