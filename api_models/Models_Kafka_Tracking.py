import datetime

import bson

from ReCompact import document
@document(
    "Sys_Kafka_Track",
    indexes=["Topic","Error","CreatedOn"]
)
class Sys_Kafka_Track:
    _id = (bson.ObjectId)
    Topic=(str)
    Data =(dict)
    CreatedOn=  (datetime.datetime)
    Error=(str)