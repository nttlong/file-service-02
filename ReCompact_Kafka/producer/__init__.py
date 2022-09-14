"""
How to use:
    1- Thee must create new Bootstrap with broker server in initial parameters, then assign to one variable.
    The variable can be use across thy application. If thy call Bootstrap again with the same broker server
    Thee will get old instance
    2- In order create a new topic just call <boostrap server variable>.producers.<topic name>.send(<dict data>)

    Example:
        my_brokers= new Bootstrap(["server 1:port1"],...)
        my_brokers.producers.topics.hello_world.topic.send({"Name":"znazi"})
        or
        getattr(my_brokers.producers.topics,"hello_world").topic.send({"Name":"znazi"})
    Example 2 print topic key:
        purchase_topic = my_brokers.producers.topics.purchase
        print(purchase_topic.topic_key) show "purchase"
        order_topic = purchase.topics.topic.order
        print(order_topic.topic_key) show "purchase.order"




"""

__static_dict__ = None

import confluent_kafka
import threading as __threading__

__lock__ = __threading__.Lock()


def __producer__(
        servers,
        delivery_report
):
    global __static_dict__
    global __lock__
    assert isinstance(servers, list), 'producer_name must be str[]'

    from confluent_kafka import Producer

    import json
    if not __static_dict__:
        __lock__.acquire()
        __static_dict__ = {}
        __lock__.release()
    producer_name = str.join(',', servers)
    delivery_report_key = "-"
    if callable(delivery_report):
        delivery_report_key = f"{delivery_report.__module__}.{delivery_report.__name__}"
    producer_key = f"{producer_name}.{delivery_report_key}"
    ret = __static_dict__.get(producer_key, None)

    if not isinstance(ret, Producer):
        __lock__.acquire()
        try:
            ret = Producer(
                {
                    "bootstrap.servers": producer_name,
                    'socket.timeout.ms': 100,
                    'api.version.request': 'false',
                    'broker.version.fallback': '0.9.0',
                }
            )
            __static_dict__[producer_key] = ret
        except Exception as e:
            raise e
        finally:
            __lock__.release()

    return ret


def __delivery_report__(err, msg):
    print(err)
    print(msg)


class Bootstrap:

    def __init__(self, bootstrap_servers, delivery_report=None):

        """
        Init bootstrap server for kafka producer
        :param bootstrap_servers: list of broker servers including port number ex:['host1:port1',...,'host n:portn']
        :param delivery_report: point to function with 2 arguments first for error second for msg
        """

        assert isinstance(bootstrap_servers, list), 'producer_name must be str[]'
        self.__bootstrap_servers__ = bootstrap_servers
        self.kafka_producer = __producer__(bootstrap_servers, delivery_report)
        if callable(delivery_report):
            if delivery_report.__code__.co_argcount < 2:
                raise Exception(f"{Bootstrap.__module__}.{Bootstrap.__name__}.__init__ \n"
                                f"with delivery_report was assign by {delivery_report.__module__}.{delivery_report.__name__} is error.\n"
                                f" why?\n"
                                f"{delivery_report.__module__}.{delivery_report.__name__} must have 2 arguments\n"
                                f"The First for error and the second fo original msg")
            self.delivery_report = delivery_report
        else:
            global __delivery_report__
            self.delivery_report = __delivery_report__

    def send_msg_async(self, topic_id, msg):
        import json
        from bson import json_util
        str_json_msg = json.dumps(msg, check_circular=False, default=json_util.default)
        self.kafka_producer.produce(
            topic_id,
            str_json_msg,
            callback=lambda err, original_msg=str_json_msg: self.delivery_report(err, original_msg
                                                                                 ),
        )
        self.kafka_producer.flush()

    def send_msg_sync(self, topic_id, msg):
        import json
        from bson import json_util
        str_json_msg = json.dumps(msg, check_circular=False, default=json_util.default)

        self.kafka_producer.produce(
            topic_id,
            str_json_msg,
            callback=lambda err, original_msg=str_json_msg: self.delivery_report(
                err, original_msg
            ),
        )
        self.kafka_producer.flush()
