import shutil

from confluent_kafka import Producer

p = Producer({'bootstrap.servers': '172.16.7.91:30992'})
p.produce('topic-001', "Chi la test".encode('utf-8'))
from confluent_kafka import Consumer
c = Consumer({
    'bootstrap.servers': '172.16.7.91:30992',
    'group.id': 'mygroup',
    'auto.offset.reset': 'earliest'
})

c.subscribe(['topic-001'])

while True:
    msg = c.poll(1.0)

    if msg is None:
        continue
    if msg.error():
        print("Consumer error: {}".format(msg.error()))
        continue

    print('Received message: {}'.format(msg.value().decode('utf-8')))
#10.244.33.243:9092 10.244.33.243
c.close()