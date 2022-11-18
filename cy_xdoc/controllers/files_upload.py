import bson
import humanize

import cy_docs
import cy_web
from cy_xdoc.auths import Authenticate
from fastapi import File, Depends, UploadFile
from cy_xdoc.controllers.models.file_upload import UploadFilesChunkInfoResult
import cy_kit
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.file_storage import FileStorageObject,FileStorageService
from cy_xdoc.services.msg import MessageService
from cy_xdoc.models.files import DocUploadRegister
import typing


@cy_web.hanlder("post", "{app_name}/files/upload")
def files_upload(app_name: str, UploadId: str, Index: int, FilePart: UploadFile,
                 token=Depends(Authenticate)) -> UploadFilesChunkInfoResult:
    content_part = FilePart.file.read()
    file_service = cy_kit.single(FileServices)
    file_storage_service = cy_kit.provider(FileStorageService)
    msg_service = cy_kit.provider(MessageService)

    upload_item = file_service.db(app_name).doc(DocUploadRegister) @ UploadId
    if upload_item is None:
        del FilePart
        del content_part
        return cy_docs.DocumentObject(
            Error=dict(
                Message="Upload was not found or has been remove",
                Code="ItemWasNotFound"

            )
        ).to_pydantic()

    file_size = upload_item.SizeInBytes
    # path_to_broker_share = os.path.join(path_to_broker_share,f"{UploadId}.{upload_item.get(docs.Files.FileExt.__name__)}")
    size_uploaded = upload_item.SizeUploaded or 0
    num_of_chunks_complete = upload_item.NumOfChunksCompleted or 0
    nun_of_chunks = upload_item.NumOfChunks or 0
    main_file_id = upload_item.MainFileId
    chunk_size_in_bytes = upload_item.ChunkSizeInBytes or 0
    server_file_name = upload_item.ServerFileName
    if num_of_chunks_complete == 0:
        fs = file_storage_service.instance.create(
            app_name=app_name,
            rel_file_path=server_file_name,
            chunk_size=chunk_size_in_bytes, size=file_size)
        fs.push(content_part, Index)
        upload_item.MainFileId = fs.get_id()
        msg_service.instance.emit(
            app_name=app_name,
            message_type="files.upload",
            data=upload_item
        )



    else:
        fs = file_storage_service.instance.get_file_by_name(
            app_name=app_name,
            rel_file_path=server_file_name
        )
        fs.push(content_part, Index)

    size_uploaded += len(content_part)
    ret = cy_docs.DocumentObject()
    ret.Data = cy_docs.DocumentObject()
    ret.Data.Percent = round((size_uploaded * 100) / file_size, 2)
    ret.Data.SizeUploadedInHumanReadable = humanize.filesize.naturalsize(size_uploaded)
    num_of_chunks_complete += 1
    ret.Data.NumOfChunksCompleted = num_of_chunks_complete
    ret.Data.SizeInHumanReadable = humanize.filesize.naturalsize(file_size)
    status = 0
    if num_of_chunks_complete == nun_of_chunks:
        status = 1
    expr: DocUploadRegister = file_service.expr(DocUploadRegister)
    file_service.db(app_name).doc(DocUploadRegister).update(
        expr.Id == UploadId,
        expr.SizeUploaded << size_uploaded,
        expr.NumOfChunksCompleted <<num_of_chunks_complete,
        expr.Status <<status,
        expr.MainFileId << bson.ObjectId(fs.get_id())
    )



    del FilePart
    return ret.to_pydantic()
