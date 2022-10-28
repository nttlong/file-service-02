import datetime
import pathlib
import os
import threading
import time

import bson
import gridfs
import pymongo.database

import ReCompact.db_async
import api_models.documents
import enig
import enig_frames.repositories.files
import enig_frames.services.file_system
import enig_frames.services.hosts
import enig_frames.services.search_engine
import enig_frames.loggers
import enig_frames.config
import enig_frames.db_logs
import enig.types


class PlugInService(enig.Singleton):
    def __init__(self,
                 repo: enig_frames.repositories.files.Files = enig.depen(
                     enig_frames.repositories.files.Files
                 ),
                 file_system: enig_frames.services.file_system.FileSystem = enig.depen(
                     enig_frames.services.file_system.FileSystem
                 ),
                 host: enig_frames.services.hosts.Hosts = enig.depen(
                     enig_frames.services.hosts.Hosts
                 ),
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 ),
                 logger: enig_frames.loggers.Loggers = enig.depen(
                     enig_frames.loggers.Loggers
                 ),
                 db_logs: enig_frames.db_logs.DbLogs = enig.depen(
                     enig_frames.db_logs.DbLogs
                 ),
                 search_service: enig_frames.services.search_engine.SearchEngineService = enig.depen(
                     enig_frames.services.search_engine.SearchEngineService
                 )):
        self.repo: enig_frames.repositories.files.Files = repo
        self.file_system = file_system
        self.host = host
        self.configuration = configuration
        self.logger = logger
        self.db_logs = db_logs
        self.search_service: enig_frames.services.search_engine.SearchEngineService = search_service

    def start(self, app_name: str, upload_id: str, file_id: str):
        if isinstance(file_id, str):
            file_id = bson.ObjectId(file_id)
        upload_info = self.repo.get_item_by_upload_id(app_name, upload_id)
        _num_of_chunks = upload_info[api_models.documents.Files.NumOfChunks]
        _db: ReCompact.db_async.DbContext = self.repo.db.context(app_name)

        expire_time_by_seconds = 60 * 60 * 8
        file_path = os.path.join(
            self.host.get_temp_upload_dir(app_name),
            f"{upload_id}.{upload_info[api_models.documents.Files.FileExt]}")

        def runner(_app_name, _upload_id: str, _file_path: str, _file_id: bson.ObjectId,
                   db: ReCompact.db_async.DbContext, _total_chunk: int):
            start_time = datetime.datetime.utcnow()
            delta_time = (datetime.datetime.utcnow() - start_time).total_seconds()
            chunk_index = 0
            while delta_time < expire_time_by_seconds and chunk_index < _total_chunk:
                fs_chunk_coll: pymongo.database.Collection = db.db.delegate.get_collection("fs.chunks")
                agg = fs_chunk_coll.aggregate(
                    [

                        {
                            "$match": {
                                "$and": [
                                    {api_models.documents.FsChunks.files_id.__name__: _file_id},
                                    {"n": {"$gte": chunk_index}},
                                ]
                            }
                        }
                    ]
                )
                ls = list(agg)
                for fs_chunk in ls:
                    if not os.path.isfile(_file_path):
                        with open(_file_path, "wb") as f:
                            f.write(fs_chunk["data"])
                            del fs_chunk["data"]
                    else:
                        with open(_file_path, "ab") as f:
                            f.write(fs_chunk["data"])
                            del fs_chunk["data"]
                    chunk_index = chunk_index + 1
                del ls
                delta_time = (datetime.datetime.utcnow() - start_time).total_seconds()
                time.sleep(0.01)
            _db.insert_one(
                api_models.documents.MediaTracking,
                api_models.documents.MediaTracking.UploadId == _upload_id,
                api_models.documents.MediaTracking.CurrentChunkIndex == chunk_index,
                api_models.documents.MediaTracking.NumOfChunks == _total_chunk

            )
            if chunk_index >= _total_chunk - 1:
                self.start_plug_ins(_app_name, _upload_id, _file_path)

        threading.Thread(target=runner, args=(app_name, upload_id, file_path, file_id, _db, _num_of_chunks,)).start()

    def start_plug_ins(self, app_name: str, upload_id, file_path):
        def run_plugin_sync(_app_name: str, _upload_id, _file_path):

            for _media_plugin in self.configuration.config.media_plugins:

                def start_plugin(media_plugin: str):
                    logger = self.logger.get_logger(media_plugin.replace(':', '--'))
                    try:
                        module_name = media_plugin.split(':')[0]
                        class_name = media_plugin.split(':')[1]
                        plugin_instance: enig_frames.plugins.base_plugin.BasePlugin = enig.create_instance_from_moudle(
                            module_name, class_name)

                        plugin_instance.process(
                            file_path=_file_path,
                            app_name=_app_name,
                            upload_id=_upload_id
                        )
                        upload_item = self.repo.get_item_by_upload_id(
                            app_name=app_name,
                            upload_id=upload_id
                        )
                        self.search_service.update_upload_register(
                            app_name=app_name,
                            id=upload_id,
                            upload_register=upload_item
                        )


                    except Exception as e:
                        self.db_log.debug(app_name, e)
                        logger.exception(e)

                threading.Thread(target=start_plugin, args=(_media_plugin,)).start()

        threading.Thread(target=run_plugin_sync, args=(app_name, upload_id, file_path)).start()
