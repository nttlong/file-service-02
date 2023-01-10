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
    "1": {
        "$contains" :['admin']
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
doc = search_services.get_doc("hps-file-test",id="c4f5cc64-7163-4155-bd6f-8f1a05442173")
# filter1=None
ret = search_services.full_text_search(
    app_name="hps-file-test",
    privileges= filter1,
    page_index=0,
    content="long test",
    page_size=10,
    highlight=False

)
hits = ret.hits
total = hits.total
for x in ret.items:
    print(x)
print(ret)



#
#
#     print(cls)

# fx = get_map(DocUploadRegister)





