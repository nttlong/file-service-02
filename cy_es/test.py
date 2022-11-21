import cy_es_x
from elasticsearch import Elasticsearch
client = Elasticsearch(hosts=["192.168.18.36:9200"])
indexes = cy_es_x.get_all_index(client)
filter_by_id = cy_es_x.docs.id=="56330233-59f2-48b9-b213-72e75f9f9b28"
filter_by_id2 = cy_es_x.docs.id=="63154d2d-035e-4b7b-8486-5c44955f933d"
filter_or =filter_by_id & filter_by_id2

filter = filter_or&(cy_es_x.docs.mark_delete==False)

ret=cy_es_x.search(
    client=client,
    index="lv-codx_hps-file-test",
    # filter= (cy_es_x.docs.id=="56330233-59f2-48b9-b213-72e75f9f9b28")|(cy_es_x.docs.mark_delete==False)
    filter = filter
)

fx=ret
