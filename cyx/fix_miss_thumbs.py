import cy_docs
import cy_kit
from cy_xdoc.services.files import FileServices
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.msg_mongodb import MessageServiceMongodb
fs:FileServices = cy_kit.singleton(FileServices)
msg:MessageServiceMongodb =cy_kit.singleton(MessageServiceMongodb)
app_name = "lv-docs"

context = fs.db_connect.db(app_name).doc(DocUploadRegister)

lst = context.context.aggregate().match(
    (context.fields.id == "328d517c-5021-44c3-8e3e-4f0c26972a28")

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