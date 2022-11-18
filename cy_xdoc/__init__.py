import fastapi
import cy_kit
import cy_xdoc.services.file_storage
import cy_xdoc.services.file_storage_mongodb

from cy_xdoc.services.apps import AppServices
from cy_xdoc.services.accounts import AccountService


import cy_xdoc.services.file_storage_disk
import cy_xdoc.services.files
import cy_xdoc.services.msg
import cy_xdoc.services.msg_mongodb
cy_kit.config_provider(
    from_class=cy_xdoc.services.file_storage.FileStorageService,
    implement_class=cy_xdoc.services.file_storage_mongodb.MongoDbFileService
)
cy_kit.config_provider(
    from_class= cy_xdoc.services.msg.MessageService,
    implement_class= cy_xdoc.services.msg_mongodb.MessageServiceMongodb
)
class libs:
    class Services:
        file_storage: cy_xdoc.services.file_storage_mongodb.FileStorageService = cy_kit.provider(
            cy_xdoc.services.file_storage.FileStorageService,
        )
        files: cy_xdoc.services.files.FileServices = cy_kit.single(cy_xdoc.services.files.FileServices)
