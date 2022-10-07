"""
API lay thong tin upload
"""

import fasty
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel, Field
import api_models.documents as docs
from typing import List, Union
from fastapi import Depends, FastAPI, HTTPException, status
from ReCompact import db_async
from fastapi import Body
import fasty.JWT


class VideoInfoClass(BaseModel):
    Width: Union[int, None] = Field(description="Resolution width")
    Height: Union[int, None] = Field(description="Resolution Height")
    Duration: Union[int, None] = Field(description="Duration time in second")


class UploadInfoResult(BaseModel):
    UploadId: Union[str, None] = Field(description="Id upload")
    FileName: Union[str, None] = Field(description="An original filename")
    FileNameOnly: Union[str, None] = Field(description="An original filename without extension")
    FileExt: Union[str, None] = Field(description="File extension")
    HasThumb: Union[bool, None] = Field(description="If thumb of this upload was generate set true")
    SizeInBytes: Union[int, None] = Field(description="File size")
    FullUrl: Union[str, None] = Field(description="Full url of content")
    RelUrl: Union[str, None] = Field(description="Relative url of content")
    UrlThumb: Union[str, None] = Field(description="Full url of thumb")
    RelUrlThumb: Union[str, None] = Field(description="Relative url of thumb")
    HasOCR: Union[bool, None] = Field(description="If ORC of this upload was generate set true")
    UrlOCR: Union[str, None] = Field(description="Url of ORC content")
    RelUrlOCR: Union[str, None] = Field(description="Relative Url of ORC content")
    UrlOfServerPath: Union[str, None] = Field(description="Full url to content")
    RelUrlOfServerPath: Union[str, None] = Field(description="Relative url to content")
    MimeType: Union[str, None] = Field(description="Mime Type")
    IsPublic: Union[bool, None] = Field(description="Access type")
    Status: Union[int, None] = Field(description="Status of upload 0: not finish yet, 1;: finished")
    VideoInfo: Union[VideoInfoClass, None] = Field(description="Thông tin media")
    AvailableThumbs:Union[type([]), None] = Field(description="All relative available thumbs")


@fasty.api_post("/{app_name}/files/info", response_model=UploadInfoResult)
async def get_info(app_name: str, request: Request,
                   token: str = Depends(fasty.JWT.oauth2_scheme), UploadId: str = Body(embed=True)):
    """
    APi này lay chi tiet thong tin cua Upload
    :param app_name:
    :return:
    """
    ret = UploadInfoResult()
    db_name = await fasty.JWT.get_db_name_async(app_name)
    if db_name is None:
        return Response(status_code=403)
    db = db_async.get_db_context(db_name)
    upload_info = await db.find_one_async(docs.Files, docs.Files._id == UploadId)
    ret.UploadId: str = upload_info["_id"]
    ret.FileName = upload_info.get(docs.Files.FileName.__name__)
    ret.FileNameOnly = upload_info.get(docs.Files.FileNameOnly.__name__)
    ret.FileExt = upload_info.get(docs.Files.FileExt.__name__)
    ret.HasOCR = upload_info.get(docs.Files.OCRFileId.__name__) is not None
    ret.MimeType = upload_info.get(docs.Files.MimeType.__name__)
    ret.SizeInBytes = upload_info.get(docs.Files.SizeInBytes.__name__)
    ret.IsPublic = upload_info.get(docs.Files.IsPublic.__name__)
    ret.Status = upload_info.get(docs.Files.Status.__name__)
    ret.RelUrl = f"api/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}"
    ret.FullUrl = f"{fasty.config.app.api_url}/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}"
    ret.HasThumb = upload_info.get(docs.Files.ThumbFileId.__name__) is not None
    available_thumbs=upload_info.get(docs.Files.AvailableThumbs.__name__,[])
    ret.AvailableThumbs=[]
    for x in available_thumbs:
        ret.AvailableThumbs+=[f"{app_name}/{x}"]
    if ret.HasThumb:
        """
        http://172.16.7.25:8011/api/lv-docs/thumb/c4eade3a-63cb-428d-ac63-34aadd412f00/search.png.png
        """
        ret.RelUrlThumb = f"api/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}.webp"
        ret.UrlThumb = f"{fasty.config.app.api_url}/{app_name}/thumb/{ret.UploadId}/{ret.FileName.lower()}.webp"
    if ret.HasOCR:
        """
        http://172.16.7.25:8011/api/lv-docs/file-ocr/cc5728d0-c216-43f9-8475-72e84b6365fd/im-003.pdf
        """
        ret.RelUrlOCR = f"api/{app_name}/file-ocr/{ret.UploadId}/{ret.FileName.lower()}.pdf"
        ret.UrlOCR = f"{fasty.config.app.api_url}/{app_name}/file-ocr/{ret.UploadId}/{ret.FileName.lower()}.pdf"
    if upload_info.get(docs.Files.VideoResolutionWidth.__name__):
        ret.VideoInfo = VideoInfoClass()
        ret.VideoInfo.Width = upload_info.get(docs.Files.VideoResolutionWidth.__name__)
        ret.VideoInfo.Height = upload_info.get(docs.Files.VideoResolutionHeight.__name__)
        ret.VideoInfo.Duration = upload_info.get(docs.Files.VideoDuration.__name__)
    return ret
