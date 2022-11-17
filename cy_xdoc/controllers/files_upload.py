import humanize

import cy_docs
import cy_web
from cy_xdoc.auths import Authenticate
from fastapi import File, Depends, UploadFile
from cy_xdoc.controllers.models.file_upload import UploadFilesChunkInfoResult
import cy_kit
from cy_xdoc.services.files import FileServices
from cy_xdoc.services.file_content import FileContentService
from cy_xdoc.services.msg import MsgService
from cy_xdoc.models.files import DocUploadRegister
import typing


@cy_web.hanlder("post", "{app_name}/files/upload")
def files_upload(app_name: str, UploadId: str, Index: int, FilePart: UploadFile,
                 token=Depends(Authenticate)) -> UploadFilesChunkInfoResult:
    file_service = cy_kit.single(FileServices)
    file_content_service = cy_kit.single(FileContentService)
    msg_service = cy_kit.single(MsgService)
    upload_item = file_service.db(app_name).doc(DocUploadRegister) @ UploadId
    if upload_item is None:
        del FilePart
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
        fs = file_content_service.create(
            app_name=app_name,
            rel_file_path=server_file_name,
            chunk_size=chunk_size_in_bytes, size=file_size)
        fs.push(FilePart, Index)
        upload_item.MainFileId = fs.Id
        msg_service.emit(
            app_name=app_name,
            message_type="files.upload",
            data=upload_item
        )



    else:
        fs = file_content_service.get_file(
            app_name=app_name,
            rel_file_path=server_file_name
        )
        fs.push(FilePart, Index)
        # save_to_file(
        #     db_context, num_of_chunks_complete, Index, server_file_name, path_to_broker_share
        # )
    size_uploaded += len(FilePart)
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
        expr.MainFileId << fs.Id
    )



    del FilePart
    return ret.to_pydantic()
