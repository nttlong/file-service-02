"""
Xử lý thum cho file pdf
"""
import config
import uuid
import ReCompact_Kafka.consumer
import logging


def handler(consumer: ReCompact_Kafka.consumer.Consumer_obj, msg, logger: logging.Logger):
    """
    Gọi xử lý bằng libre office
    :param consumer:
    :param msg:
    :return:
    """
    import config
    import os

    data = consumer.get_json(msg)

    file_path = data["FilePath"]  # Đường dẫn đến file vật lý
    logger.info(f"Create PDF Thumb file {file_path}")
    logger.info(data)
    import ntpath
    file_name = ntpath.basename(file_path)
    file_name_on_ly, file_ext = os.path.splitext(file_name)
    upload_info = data["UploadInfo"]  # Thông tin lúc upload
    app_name = data["AppName"]  # Tên App
    server_file_name = upload_info["ServerFileName"]
    out_put_dir = os.path.join(config.temp_thumbs, app_name)
    if not os.path.isdir(out_put_dir):
        os.mkdir(out_put_dir)
    image_file_path = os.path.join(out_put_dir, f"{file_name_on_ly}.png")  # Đường dẫn đầu đủ đến file image
    if not os.path.isfile(image_file_path):
        """
        Nếu ảnh file ảnh của pdf chưa có
        Hoặc vì một lý do nào đó tạo nhưng đa mất
        """
        import glob, sys, fitz

        # To get better resolution
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        all_files = glob.glob(file_path)

        for filename in all_files:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap()  # render page to an image
                pix.save(image_file_path)  # store image as a PNG
                break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
            break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
    thumb_file_path = os.path.join(out_put_dir, f"{file_name_on_ly}_thumb.png")
    if not os.path.isfile(thumb_file_path):
        ThumbWidth, ThumbHeight = upload_info.get('ThumbWidth', 700), upload_info.get('ThumbHeight', 700)
        """
        Dòng tren lay kích thươc cua thumb
        Anh thum thuc su se co lai vua van voi khung
        
        """
        from PIL import Image

        basewidth = 300
        img = Image.open(image_file_path)
        w, h = img.size
        rate = ThumbWidth / w  # Mặc dịnh bóp theo bề rộng
        if h > w:  # Nhưng vì bề dọc lớn hơn bề rộng
            rate = ThumbHeight / h  # nên bóp theo bề dọc
        nh = int((float(h) * float(rate)))
        nw = int((float(w) * float(rate)))
        img = img.resize((nw, nh), Image.ANTIALIAS)
        thumb_file_path = os.path.join(out_put_dir, f"{file_name_on_ly}_thumb.png")

        img.save(thumb_file_path)
    """
    Cất vào database mongodb
    """
    import ReCompact.db_context
    import mongo_db
    db = mongo_db.get_db(app_name)
    fs = ReCompact.db_context.create_mongodb_fs_from_file(
        db=db,
        full_path_to_file=thumb_file_path,
        chunk_size=1024 * 1024 * 2,

    )
    import api_models.Model_Files
    import ReCompact.dbm.DbObjects
    import ReCompact.dbm

    ReCompact.dbm.DbObjects.update(
        db=db,
        data_item_type=api_models.Model_Files.DocUploadRegister,
        filter=ReCompact.dbm.FILTER.ServerFileName == server_file_name,
        updator=ReCompact.dbm.SET(
            ReCompact.dbm.FIELDS.ThumbFileId == fs._id,
            ReCompact.dbm.FIELDS.HasThumb == True
        )

    )
    consumer.commit(msg)

    logger.info(f"Thumb of {upload_info['_id']} with {upload_info['FileName']} has been created")
    logger.info(f"Create PDF Thumb file {file_path} is finish")
    logger.info(data)

def error(err,msg,logger:logging.Logger):
    logger.debug(err)


__id__ = str(uuid.uuid4())



consumer = ReCompact_Kafka.consumer.create(
    topic_id="files.services.upload.thumb.pdf",
    group_id=f"files.services.upload.thumb.pdf.{__id__}",
    server=config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,

)

if __name__ == "__main__":
    consumer.run()

#C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumers\file_services_upload_thumb_pdf.py