from torch.distributed.autograd import context

import cy_docs
import cy_kit
from cy_xdoc.services.files import FileServices
from cy_xdoc.models.files import DocUploadRegister
from cyx.common.msg_mongodb import MessageServiceMongodb
fs:FileServices = cy_kit.singleton(FileServices)
msg:MessageServiceMongodb =cy_kit.singleton(MessageServiceMongodb)
app_name = "hps-file-test"

context = fs.db_connect.db(app_name).doc(DocUploadRegister)

lst = context.context.aggregate().match({}
    # context.fields.id=="4cff02f0-5b2f-4b95-99a8-440884d9ce3e"
    # ((context.fields.FileExt == "png")|(context.fields.FileExt == "jpg")) & (context.fields.OCRFileId==None) &(context.fields.Status==1)


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