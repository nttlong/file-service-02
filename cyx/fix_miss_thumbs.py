import cy_docs
import cy_kit
from cy_xdoc.services.files import FileServices
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.msg_mongodb import MessageServiceMongodb
fs:FileServices = cy_kit.singleton(FileServices)
msg:MessageServiceMongodb =cy_kit.singleton(MessageServiceMongodb)
app_name = "hps-file-test"

context = fs.db_connect.db(app_name).doc(DocUploadRegister)

lst = context.context.aggregate().match(
    (context.fields.id == "31747044-7484-4674-b013-b39d3e2e9b30")

).sort(
    context.fields.RegisterOn.desc()
).limit(100)

for x in lst:
    msg.emit(
        app_name=app_name,
        data= x,
        message_type='files.upload'
    )

    print(x)