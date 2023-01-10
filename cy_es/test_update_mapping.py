import cy_es
import elasticsearch
client = elasticsearch.Elasticsearch(
    hosts=["172.16.7.91:30920/"]
)
fx =cy_es.cy_es_x.docs.content
vx = cy_es.create_mapping(
    [
        cy_es.set_norms(cy_es.buiders.content,"text",False)
    ]
)

app_name="hps-file-test"
cy_es.cy_es_x.create_index(
    client=client,
    index= f"lv-codx-v2_{app_name}",
    body= vx
)
cy_es.put_mapping(
    client=client,
    index =f"lv-codx_{app_name}",
    body = vx
)
cy_es.cy_es_x.clone_index(client=client,from_index=f"lv-codx_{app_name}",to_index=f"lv-codx-v2_{app_name}",segment_size=5)
print(vx)
print(client)
"""
from elasticsearch import Elasticsearch

self.elastic_con = Elasticsearch([host], verify_certs=True)
mapping = '''
{  
  "mappings":{  
    "properties": {
    "title": {
      "type": "text",
      "norms": false
    }
  }
  
}'''
self.elastic_con.indices.create(index='test-index', ignore=400, body=mapping)
"""
cy_es.cy_es_x.create_index()