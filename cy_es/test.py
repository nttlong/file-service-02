import cy_es_x
from elasticsearch import Elasticsearch
from cy_xdoc.models.files import DocUploadRegister
client = Elasticsearch(hosts=["192.168.18.36:9200"])
index ="lv-codx_hps-file-test"

filter=(cy_es_x.docs.mark_delete==False) & cy_es_x.match_phrase(
    cy_es_x.docs.content,"demo xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)

ret= cy_es_x.search(
    client=client,
    index=index,
    filter=filter,
    limit=10
)
hits = ret.hits
total = hits.total
print(ret)



#
#
#     print(cls)

# fx = get_map(DocUploadRegister)





