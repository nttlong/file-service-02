import pathlib
working_dir = str(pathlib.Path(__file__).parent.absolute())
import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))
sys.path.append(str(pathlib.Path(__file__).parent.parent.parent.absolute()))
import os
is_debug = True
kafka_broker = ["192.168.18.36:9092"]
office_extension = ";docx;doc;xls;xlsx;txt;pdf;ppx;pptx;json;psd;html;xml;js;otg;svg;vsd;" \
    .split(';');
office_extension += ".ODT;.CSV;.DB;.DOC;.DOCX;.DOTX;.FODP;.FODS;.FODT;.MML" \
                    ";.ODB;.ODF;.ODG;.ODM;.ODP;.ODS;.OTG;.OTP;.OTS;.OTT;.OXT" \
                    ";.PPTX;.PSW;.SDA;.SDC;.SDD;.SDP;.SDW;.SLK;.SMF;.STC" \
                    ";.STD;.STI;.STW;.SXC;.SXG;.SXI;.SXM;.UOF;.UOP;.UOS;.UOT" \
                    ";.VSD;.VSDX;.WDB;.WPS;.WRI;.XLS;.XLSX".lower().split(';.')
temp_thumbs = r"\\192.168.18.36\Share\DjangoWeb\temp_thumb"  # Thư mục tạm để xử lý ảnh thumbs

poppler_path = r"C:\dj-apps\jd-apps\poppler-0.68.0\bin"
"""
Thư mục quan trọng Libre office khai báo dưới đây
"""
libre_office_path = r"C:\Program Files\LibreOffice\program\soffice.exe"

temp_libre_office_user_profile_dir = os.path.join(working_dir, "LibreOfficeTempProfiles")
"""
Thư mục tạm profile để cho phép LibreOffice chạy song song khai báo dưới đây
"""
if not os.path.isdir(temp_libre_office_user_profile_dir):
    os.makedirs(temp_libre_office_user_profile_dir)
fs_crawler_path =r"\\192.168.18.36\fscrawler-es7-2.9\docs"
"""
Thư mục dành cho fs_crawler
Để đánh Elastich search trên nội dung văn bản hệ thống này đang dùng 1 tiến trình ngoại vi
(Hệ thống không kiểm soát được) gọi là fscrawler phiên bản 7-2.9
fs-crawler sẽ tự động quét thư mục dưới đây sau mỗi 24 phút (đây là thời gian mặc định, tuy nhiên vẫn có thể cấu hình lại)
Vì vậy việc tạo index cho elastic search chỉ đơn giản là bỏ file vào thư mục dưới đây
Thành công hay thất bại phải vào logs của fs-crawler xem 
"""


"""
Thư mục tạm để xử lý orc
"""
tmp_dir_ocr =r"\\192.168.18.36\Share\DjangoWeb\ocr"


import os

if not os.path.isdir(temp_thumbs):
    raise Exception(f"'{temp_thumbs}' was not found")
# if  not os.path.isdir(poppler_path):
#     raise Exception(f"'{poppler_path}' was not found")
if not os.path.isfile(libre_office_path):
    raise Exception(f"'{libre_office_path}' was not found"
                    f"Thee need LibreOffice fo office file convert")
if not os.path.isdir(temp_libre_office_user_profile_dir):
    raise Exception(f"'{temp_libre_office_user_profile_dir}' was not found"
                    f"Need Temporary profile folder for Libre Office when it run in parallel")
if not os.path.isdir(fs_crawler_path):
    raise Exception(f"'{fs_crawler_path}' was not found"
                    f"The directory for fs-crawler scan every 24 minutes in default")
if not os.path.isdir(tmp_dir_ocr):
    raise Exception(f"'{tmp_dir_ocr}' was not found"
                    f"The directory for result of OCR processing")
mongo_db_config = dict(

    host=["192.168.18.36"],
    port=27018,
    username="admin-doc",
    password="123456",
    authSource="lv-docs",
    authMechanism="SCRAM-SHA-1",
    # replicaSet="rs0"

)
# import re_process.mongo_db
# db = re_process.mongo_db.get_db(mongo_db_config["authSource"])
# import  uuid
# col_name =  str(uuid.uuid4())
# try:
#     db.get_collection(col_name).insert_one({})
# except Exception as e:
#     raise Exception("Can not connect to mongo db "+e)
lang_processing = [
    'vie',
    'eng'
]