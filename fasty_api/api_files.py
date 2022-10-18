"""
API liệt kê danh sách các file
"""
import datetime
import re
from time import strftime
from time import gmtime
import ReCompact.dbm
import enig
import enigma
import fasty
from fastapi import FastAPI, Request, Response
from pydantic import BaseModel
import api_models.documents as docs
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from ReCompact import db_async
import json

from . import api_files_schema
import humanize.time
import fasty.JWT
from pathlib import Path
import enig_frames.containers
import enig_frames.services.applications
import enig_frames.containers

@fasty.api_post("/{app_name}/files")
async def get_list_of_files(app_name: str, filter: api_files_schema.Filter, request: Request,
                            token: str = Depends(fasty.JWT.oauth2_scheme)):
    """
    APi này sẽ liệt kê danh sách các file
    :param filter:
    :param app_name:
    :return:
    """
    container= enig_frames.containers.Container
    db_name = container.db_context.get_db_name(app_name)
    if db_name is None:
        return Response(status_code=403)
    db = db_async.get_db_context(db_name)
    agg = db.aggregate(docs.Files)
    agg.project(
        # docs.Files._id,
        docs.Files.FileName,
        docs.Files.FullFileName,
        docs.Files.HasThumb,
        docs.Files.ServerFileName,
        docs.Files.SizeInHumanReadable,
        docs.Files.Status,
        docs.Files.MimeType,
        docs.Files.IsPublic,
        docs.Files.HasThumb,
        docs.Files.OCRFileId,
        docs.Files.PdfFileId,
        docs.Files.AvailableThumbs,
        FileSize=docs.Files.SizeInBytes,
        ModifiedOn=docs.Files.LastModifiedOn,
        UploadId=docs.Files._id,
        CreatedOn=docs.Files.RegisterOn,
        Media=dict(
            Height=docs.Files.VideoResolutionHeight,
            Width=docs.Files.VideoResolutionWidth,
            Duration=docs.Files.VideoDuration,
            FPS=docs.Files.VideoFPS
        )

    )
    if filter.ValueSearch and filter.ValueSearch != "":
        agg.match(
            docs.Files.FileName == re.compile(filter.ValueSearch)
        )

    agg.sort(
        ReCompact.dbm.FIELDS.ModifiedOn.desc(),
        ReCompact.dbm.FIELDS.CreatedOn.desc(),
        ReCompact.dbm.FIELDS.FileSize.desc()

    ).pager(
        filter.PageIndex, filter.PageSize
    )

    ret_list = await agg.to_list_async()
    url = enigma.get_root_api_url()

    for x in ret_list:
        if x[docs.Files.FileNameOnly] is None:
            file_name_only = Path(x[docs.Files.FileName]).stem
            await db.update_one_async(
                docs.Files,
                docs.Files._id == x["UploadId"],
                docs.Files.FileNameOnly == file_name_only
            )
            x[docs.Files.FileNameOnly.__name__] = file_name_only
        if x.get(docs.Files.RegisterOnDays.__name__, None) is None:
            date_val = x.get(docs.Files.RegisterOn.__name__, None)
            if date_val is not None and isinstance(date_val, datetime.datetime):
                await  db.update_one_async(
                    docs.Files,
                    docs.Files._id == x["UploadId"],
                    docs.Files.RegisterOnDays == date_val.day,
                    docs.Files.RegisterOnMonths == date_val.month,
                    docs.Files.RegisterOnYears == date_val.year,
                    docs.Files.RegisterOnHours == date_val.hour,
                    docs.Files.RegisterOnMinutes == date_val.minute,
                    docs.Files.RegisterOnSeconds == date_val.second
                )
        full_filename_without_extenstion = x.get(docs.Files.FullFileNameWithoutExtenstion.__name__)
        if x.get(docs.Files.FullFileNameWithoutExtenstion.__name__) is None:
            full_filename = x.get(docs.Files.FullFileName.__name__)
            full_dir_path = str(Path(full_filename).parent)
            filename_only = Path(full_filename).stem
            full_filename_without_extenstion = f"{full_dir_path}/{filename_only}"
            await  db.update_one_async(
                docs.Files,
                docs.Files._id == x["UploadId"],
                docs.Files.FullFileNameWithoutExtenstion == full_filename_without_extenstion,
                docs.Files.FullFileNameWithoutExtenstionLower == full_filename_without_extenstion.lower(),
            )
        if x[docs.Files.FullFileNameLower] is None:
            full_filename = x[docs.Files.FullFileName]

            await  db.update_one_async(
                docs.Files,
                docs.Files._id == x["UploadId"],
                docs.Files.FullFileNameLower == full_filename.lower()
            )
        x["UrlOfServerPath"] = url + f"/{app_name}/file/{x[docs.Files.FullFileName]}"
        x["AppName"] = app_name
        x["RelUrlOfServerPath"] = f"/{app_name}/file/{x[docs.Files.FullFileName]}"
        x["ThumbUrl"] = url + f"/{app_name}/thumb/{x['UploadId']}/{x[docs.Files.FileName]}.webp"
        if x.get("Media") and x["Media"].get("Duration"):
            x["DurationHumanReadable"] = strftime("%H:%M:%S", gmtime(x["Media"]["Duration"]))
        if x[docs.Files.OCRFileId]:
            """
            /{app_name}/file-ocr/{directory:path}
            """
            x[docs.Files.OCRFileId] = None
            x["OcrContentUrl"] = url + f"/{app_name}/file-ocr/{full_filename_without_extenstion}.pdf"
        if x[docs.Files.PdfFileId]:
            x["PdfContentUrl"] = url + f"/{app_name}/file-pdf/{full_filename_without_extenstion}.pdf"
        available_thumbs = x.get(docs.Files.AvailableThumbs, [])
        a_t = []
        for ux in available_thumbs:
            a_t += [f"api/{app_name}/{ux}"]
        x[docs.Files.AvailableThumbs] = a_t

    return ret_list
