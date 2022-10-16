# """
# Consumer for upload file
# Everytime when files.services is upload with successful producer 'file_upload' topic
# How to use:
#     import re_process.consum_upload_file
#     re_process.consum_upload_file.int(
#
#     )
# """
#
# __consumer__ = None
# __on_process__ = None
# __on_error__ = None
# topic_key ="files.services.upload"
# office_extension= ";docx;doc;xls;xlsx;txt;pdf;ppx;pptx;json;psd;html;xml;js;otg;svg;vsd;"\
#     .split(';');
# office_extension+= ".ODT;.CSV;.DB;.DOC;.DOCX;.DOTX;.FODP;.FODS;.FODT;.MML" \
#                    ";.ODB;.ODF;.ODG;.ODM;.ODP;.ODS;.OTG;.OTP;.OTS;.OTT;.OXT" \
#                    ";.PPTX;.PSW;.SDA;.SDC;.SDD;.SDP;.SDW;.SLK;.SMF;.STC" \
#                    ";.STD;.STI;.STW;.SXC;.SXG;.SXI;.SXM;.UOF;.UOP;.UOS;.UOT" \
#                    ";.VSD;.VSDX;.WDB;WPS;.WRI;.XLS;.XLSX".lower().split(';.')
#
#
#
# def init(configuration, on_process, on_error):
#
#     """
#     Khở tạo consumer xử lý file upload
#     Chạy với topic "file.services.upload"
#     :param configuration:
#     :param on_process:
#     :param on_error:
#     :return:
#     """
#
#     import ReCompact_Kafka.consumer
#     global __consumer__
#     global __on_error__
#     global __on_process__
#     assert callable(on_process), 'on_process must be a function'
#     assert callable(on_error), 'on_error must ne a function'
#     assert on_process.__code__.co_argcount ==2, 'Thee must declare on_process with 1 params' \
#                                                 'the first is consumer second is msg'
#     assert on_error.__code__.co_argcount == 1, 'Thee must declare on_error with 1 params' \
#                                                'the first is consumer second is msg'
#
#     __on_error__ = on_error
#     __on_process__ = on_process
#     __consumer__ = ReCompact_Kafka.consumer.Consumer_obj(configuration)
#
# def get_consumer():
#     global __consumer__
#     return  __consumer__
# def start():
#
#     """
#     Giám sát topic 'files.services.upload'
#     :return:
#     """
#
#     import ReCompact_Kafka.consumer
#     global __consumer__
#     assert isinstance(__consumer__,
#                       ReCompact_Kafka.consumer.Consumer_obj), 'error __consumer__ mus be ' \
#                                                               'ReCompact_Kafka.consumer.Consumer_obj '
#     global __on_error__
#     global __on_process__
#     __consumer__.watch_topic(
#         topic_key="files.services.upload",
#         on_error=__on_error__,
#         handler=__on_process__
#     )
