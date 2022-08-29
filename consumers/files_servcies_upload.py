"""
File này khai báo 1 handler dùng để bắt sự kiện file upload tùy theo loại file mà hệ thống sẽ trigger các sự kiện khác
Hiện tại:



"""
import json
import logging

topic_key = "files.services.upload"
import config


def handler(consumer, msg, logger):
    """

    :type msg: object
    """

    import ReCompact_Kafka.consumer
    import ReCompact_Kafka.producer

    assert isinstance(consumer, ReCompact_Kafka.consumer.Consumer_obj)
    data = consumer.get_json(msg)
    print(consumer.get_topic_id(msg))
    import json
    print(json.dumps(data))
    import ReCompact_Kafka.consumer
    producer = ReCompact_Kafka.producer.Bootstrap(
        bootstrap_servers=consumer.broker

    )
    assert isinstance(consumer, ReCompact_Kafka.consumer.Consumer_obj)
    data = consumer.get_json(msg)

    upload_info = data["UploadInfo"]
    file_name = upload_info["FileName"]
    mime_type = upload_info["MimeType"]
    file_ext = upload_info["FileExt"]
    if file_ext in consumers.config.office_extension:
        logger.debug(f"kafka raise event {msg.topic()}.elastic")
        producer.send_msg_sync(f"{msg.topic()}.elastic", data)
        logger.debug(f"kafka raise event {msg.topic()}.thumb.office")
        producer.send_msg_sync(f"{msg.topic()}.thumb.office", data)
        logger.debug(f"kafka raise event {msg.topic()}.pdf.office")
        producer.send_msg_sync(f"{msg.topic()}.pdf.office", data)
        consumer.commit(msg)
        return
    if '/pdf' in mime_type:
        producer.send_msg_sync(f"{msg.topic()}.ocr.pdf", data)
        logger.debug(f"kafka raise event {msg.topic()}.ocr.pdf")
        producer.send_msg_sync(f"{msg.topic()}.thumb.pdf", data)
        logger.debug(f"kafka raise event {msg.topic()}.thumb.pdf")
        logger.debug(data)
        consumer.commit(msg)
        return
    if 'image/' in mime_type:
        logger.debug(f"{msg.topic()}.ocr.image", data)
        producer.send_msg_sync(f"{msg.topic()}.ocr.image", data)
        logger.debug(f"{msg.topic()}.thumb.image", data)
        producer.send_msg_sync(f"{msg.topic()}.thumb.image", data)
        logger.debug(data)
    if (isinstance(file_ext, str)
        and (file_ext[0] == '.'
        and file_ext[1:] in consumers.config.office_extension) \
        or file_ext[1:] in consumers.config.office_extension)\
            or file_ext in consumers.config.office_extension:
        logger.debug(f"kafka raise event {msg.topic()}.elastic")
        producer.send_msg_sync(f"{msg.topic()}.elastic", data)
        logger.debug(f"kafka raise event {msg.topic()}.thumb.office")
        producer.send_msg_sync(f"{msg.topic()}.thumb.office", data)
        import json
        logger.info(json.dumps(data))
    if 'video/' in mime_type:
        logger.debug(f"kafka raise event {msg.topic()}.thumb.video")

        producer.send_msg_sync(f"{msg.topic()}.thumb.video", data)
        logger.debug(data)
    consumer.commit(msg)


def error(err, msg, logger: logging.Logger):
    logger.debug(err)
    print(err)


import uuid

import ReCompact_Kafka.consumer
import consumers.config

id = str(uuid.uuid4())
consumer = ReCompact_Kafka.consumer.create(
    topic_id=topic_key,
    group_id=f"files.services.upload.{id}",
    server=consumers.config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,

)
if __name__ == '__main__':
    """
        Nếu chạy file này một cách độc lập
    """
    consumer.run()

# C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumers\file_servcies_upload.py
