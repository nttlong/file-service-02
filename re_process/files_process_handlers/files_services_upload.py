def handler(consumer,msg,logger ):
    import ReCompact_Kafka.consumer
    import ReCompact_Kafka.producer
    import re_process.config
    assert isinstance(consumer,ReCompact_Kafka.consumer.Consumer_obj)
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
    producer.send_msg_sync(f"{msg.topic()}.thumb", data)

    if '/pdf' in mime_type:
        producer.send_msg_sync(f"{msg.topic()}.ocr.pdf", data)
        logger.info(f"kafka raise event {msg.topic()}.ocr.pdf")
        producer.send_msg_sync(f"{msg.topic()}.thumb.pdf", data)
        logger.info(f"kafka raise event {msg.topic()}.thumb.pdf")
        consumer.commit(msg)
        return
    if 'image/' in mime_type:
        producer.send_msg_sync(f"{msg.topic()}.ocr.image", data)
        producer.send_msg_sync(f"{msg.topic()}.thumb.image", data)
    if file_ext in re_process.config.office_extension:
        logger.info(f"kafka raise event {msg.topic()}.elastic")
        producer.send_msg_sync(f"{msg.topic()}.elastic", data)
        logger.info(f"kafka raise event {msg.topic()}.thumb.office")
        producer.send_msg_sync(f"{msg.topic()}.thumb.office", data)
    if 'video/' in mime_type:
        logger.info(f"kafka raise event {msg.topic()}.thumb.video")
        print(f"kafka raise event {msg.topic()}.thumb.video")
        producer.send_msg_sync(f"{msg.topic()}.thumb.video", data)
    consumer.commit(msg)


def error(err,msg,logger):
    print(err)