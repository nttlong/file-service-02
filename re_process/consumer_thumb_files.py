import consum_upload_file
import ReCompact_Kafka.consumer
import config

def error_topic(msg):
    fx = msg
    print(fx)

import ReCompact_Kafka.producer
producer = ReCompact_Kafka.producer.Bootstrap(
    bootstrap_servers= config.kafka_broker

)
def process_topic(consumer, msg):
    import ReCompact_Kafka.consumer
    assert isinstance(consumer, ReCompact_Kafka.consumer.Consumer_obj)
    print(consumer.config['group.id'])
    # import json
    # import re_process.consum_upload_file
    # msg_value_dict = json.loads(
    #     msg.value().decode("utf-8")
    # )
    # upload_info = msg_value_dict["UploadInfo"]
    # file_name = upload_info["FileName"]
    # mime_type = upload_info["MimeType"]
    # file_ext = upload_info["FileExt"]
    # producer.send_msg_sync(f"{msg.topic()}.thumb", msg_value_dict)
    #
    # if '/pdf' in mime_type:
    #     producer.send_msg_sync(f"{msg.topic()}.ocr.pdf", msg_value_dict)
    #     producer.send_msg_sync(f"{msg.topic()}.thumb.pdf", msg_value_dict)
    # if 'image/' in mime_type:
    #     producer.send_msg_sync(f"{msg.topic()}.ocr.image", msg_value_dict)
    #     producer.send_msg_sync(f"{msg.topic()}.thumb.image", msg_value_dict)
    # if file_ext in re_process.consum_upload_file.office_extension:
    #     producer.send_msg_sync(f"{msg.topic()}.elastic", msg_value_dict)
    #     producer.send_msg_sync(f"{msg.topic()}.thumb.office", msg_value_dict)
    # consumer.comit(msg)


import datetime
g_id= datetime.datetime.now().isoformat('-')
consumer = ReCompact_Kafka.consumer.Consumer_obj(
    {
        'bootstrap.servers': '192.168.18.36:9092',
         'group.id': f'client.files.services.process.{g_id}',
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False
     }
)
consumer.watch_topic(
    on_error=error_topic,
    topic_key="files.services.upload..thumb.pdf",
    handler= process_topic
)

# consum_upload_file.get_consumer().reset_all_group(consum_upload_file.topic_key)
import threading
th = threading.Thread(
    target= consumer.watch_topic,
    args=(
        "files.services.upload..thumb.pdf",
        process_topic,
        error_topic
    )
)
th.start()
th.join();

