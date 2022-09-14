import ReCompact_Kafka.consumer
c = ReCompact_Kafka.consumer.Consumer_obj({
    'bootstrap.servers': '192.168.18.36:9092',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': False
})
print(c.get_all_topics_keys())
