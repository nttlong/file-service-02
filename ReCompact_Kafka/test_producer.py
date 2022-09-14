import producer
def delivery_report(err,msg):
    print(err)
    print(msg)
bootstrap = producer.Bootstrap(
    ["192.168.18.36:9092"],
    delivery_report= delivery_report
)
import datetime

bootstrap.send_msg_sync(
    topic_id="Hello world",
    msg=    dict(
        message="Yes",
        create_on= datetime.datetime.now()
    )
)