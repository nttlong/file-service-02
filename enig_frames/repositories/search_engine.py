import enig
import enig_frames.config
from elasticsearch import Elasticsearch


class SearchEngineRepo(enig.Singleton):
    def __init__(
            self,
            configuration: enig_frames.config.Configuration = enig.depen(
                enig_frames.config.Configuration
            )):
        self.configuration: enig_frames.config.Configuration = configuration
        self.es_server = self.configuration.config.elastic_search.server
        if isinstance(self.es_server,str):
            self.es_server=self.es_server.split(',')
        self.es_client = Elasticsearch(
            self.es_server,
            http_auth=["elastic", "changeme"],
        )

    def create_doc(self,id:str, index_name, body:dict):
        check = self.es_client.exists(index=index_name, id=id)
        if check.body == True:
            self.es_client.delete(index=index_name,id=id)
        ret=self.es_client.create(id=id,index=index_name, body=body)
        return ret

    def do_full_text_search(self, index_name, page_size, page_index, content):
        str_content = content
        highlight = {
            "pre_tags": ["<em>"],
            "post_tags": ["</em>"],
            "fields": {
                "content": {}
            }
        }
        match_phraseBody = {
            "match_phrase": {
                "content": {
                    "query": str_content,
                    "slop": 3,
                    "analyzer": "standard",
                    "zero_terms_query": "none",
                    "boost": 4.5
                }
            }
        }
        f_mark_dele = {"match": {"mark_delete": False}}
        f_not_exist_mark_dele = {"bool": {"must_not": {"exists": {'field': 'mark_delete'}}}}
        filter_by_mark_delete = {
            "bool": {
                "should": [f_mark_dele, f_not_exist_mark_dele]}
        }

        search_body_2 = {
            "match": {
                "content": {
                    "query": str_content,
                    "boost": 0.5

                }
            }
        }
        search_body = {
            "multi_match": {
                "query": str_content,
                "fields": ["content"],
                "type": "phrase"
            }
        }
        should_body = {
            "bool": {
                "should": [
                    match_phraseBody,
                    search_body_2,

                    # search_body

                ]
            }
        }

        bool_body = {
            "bool": {
                "must": [

                    should_body,
                    filter_by_mark_delete

                ]

            }
        }
        from_ = page_size * page_index

        resp = self.es_client.search(
            index=index_name,
            query=bool_body,
                highlight=highlight,
                from_=from_,
                size=page_size
        )

        total_items = resp['hits']['total']['value']
        max_score = resp["hits"].get('max_score')
        ret_list = []
        for hit in resp['hits']['hits']:
            highlight_contents = hit["highlight"].get('content', [])
            res_content = hit["_source"].get('content')
            score = hit.get("score")
            file_name = hit["_source"].get("file_name")
            ret_list.append(dict(
                id=hit["_id"],
                highlight=highlight_contents,
                content=res_content,
                score=score,
                file_name=file_name,  # Tên file,
                data_item= hit["_source"].get("data_item")
            ))
        return dict(
            total_items=total_items,
            max_score=max_score,
            items=ret_list,
            text_search=content
        )

    def remove_doc(self, index_name, id):
        check= self.es_client.exists(index=index_name,id=id)
        if check.body==True:
            ret = self.es_client.delete(index=index_name,id=id)
            return check.body
        return False

    def mark_delete(self, index_name:str,  id:str,mark_delete_value:bool):

        ret=self.es_client.update(
            index=index_name,
            id=id,
            body=dict(
                doc=dict(
                    mark_delete=mark_delete_value
                )
            )
        )
        return ret

