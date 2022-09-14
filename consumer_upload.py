"""
File này khai báo 1 handler dùng để bắt sự kiện file upload tùy theo loại file mà hệ thống sẽ trigger các sự kiện khác
Hiện tại:



"""

import logging

topic_key = "files.services.upload"
import consumers.config

def handler(consumer, msg, logger):
    """

    :type msg: object
    """
    import ReCompact_Kafka.consumer
    import ReCompact_Kafka.producer

    assert isinstance(consumer, ReCompact_Kafka.consumer.Consumer_obj)
    data = consumer.get_json(msg)
    print(consumer.get_topic_id(msg))
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
    try:
        producer.send_msg_sync(f"{msg.topic()}.thumb", data)
    except Exception as e:
        logger.debug(e)

    if '/pdf' in mime_type:
        producer.send_msg_sync(f"{msg.topic()}.ocr.pdf", data)
        logger.info(f"kafka raise event {msg.topic()}.ocr.pdf")
        producer.send_msg_sync(f"{msg.topic()}.thumb.pdf", data)
        logger.info(f"kafka raise event {msg.topic()}.thumb.pdf")
        consumer.commit(msg)
        return
    if 'image/' in mime_type:
        logger.info(f"{msg.topic()}.ocr.image", data)
        producer.send_msg_sync(f"{msg.topic()}.ocr.image", data)
        logger.info(f"{msg.topic()}.thumb.image", data)
        producer.send_msg_sync(f"{msg.topic()}.thumb.image", data)
    if file_ext in consumers.config.office_extension:
        logger.info(f"kafka raise event {msg.topic()}.elastic")
        producer.send_msg_sync(f"{msg.topic()}.elastic", data)
        logger.info(f"kafka raise event {msg.topic()}.thumb.office")
        producer.send_msg_sync(f"{msg.topic()}.thumb.office", data)
    if 'video/' in mime_type:
        logger.info(f"kafka raise event {msg.topic()}.thumb.video")
        print(f"kafka raise event {msg.topic()}.thumb.video")
        producer.send_msg_sync(f"{msg.topic()}.thumb.video", data)
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

#C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumer_upload.py