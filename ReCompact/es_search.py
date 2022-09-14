from elasticsearch import Elasticsearch
import threading

__nodes__ = None
__index__ = None
__lock__ = threading.Lock()
__client__ = None


def set_config(nodes, index):
    global __nodes__
    global __index__
    __nodes__ = nodes
    __index__ = index


def get_client() -> Elasticsearch:
    global __client__
    global __lock__
    global __nodes__
    if __client__ is None:
        __lock__.acquire()
        try:
            __client__ = Elasticsearch(hosts=__nodes__)
        finally:
            __lock__.release()
    return __client__

