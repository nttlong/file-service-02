import datetime

import cy_es_x
from elasticsearch import Elasticsearch
from cy_xdoc.models.files import DocUploadRegister
client = Elasticsearch(hosts=["192.168.18.36:9200"])
index ="lv-codx_long-test-123"
class A:
    def __contains__(self, item):
        print(item)
        return {"A":1}
fx= [1,2,3] in A()
filter=(cy_es_x.docs.mark_delete==False) & ((cy_es_x.docs.privileges.users.contains('hthan','tqcuong'))|(cy_es_x.docs.privileges.group.contains('nhom_a')))
import cy_kit
import cy_xdoc.services.search_engine
search_services:cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(cy_xdoc.services.search_engine.SearchEngine)
filter1 = {
    "departments": {
        "$contains" :['dcs']
    }
}
json_filter = {
    "$and": [
            {
                "$not":{
                "users": {
                    "$contains": ['hthan', 'tqcuong']
                }}
            },
            {
                "group": ['nhom_a', 'nhom_b']
            }
    ]
}

# filter1=None
ret = search_services.full_text_search(
    app_name="codx-aws",
    privileges= filter1,
    page_index=0,
    content=r"writing this letter",
    page_size=10,
    highlight=False

)
hits = ret.hits
total = hits.total
for x in ret.items:
    print(x.id)
print(ret)



#
#
#     print(cls)

# fx = get_map(DocUploadRegister)





