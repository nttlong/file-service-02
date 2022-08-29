
from confluent_kafka.admin import AdminClient


conf = {'bootstrap.servers': '192.168.18.36:9092'}
kadmin = AdminClient(conf)
# data= kadmin.poll(1000)
lst=kadmin.list_topics().topics
print(lst)