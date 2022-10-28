import threading

import enig
import enig_frames.config
import enig_frames.db_logs
from elasticsearch import Elasticsearch


class SearchEngineRepo(enig.Singleton):
    def __init__(
            self,
            configuration: enig_frames.config.Configuration = enig.depen(
                enig_frames.config.Configuration
            ),
            db_log: enig_frames.db_logs.DbLogs = enig.depen(
                enig_frames.db_logs.DbLogs
            )):
        self.configuration: enig_frames.config.Configuration = configuration
        self.es_server = self.configuration.config.elastic_search.server
        self.db_log: enig_frames.db_logs.DbLogs = db_log
        self.doc_type = "_doc"
        self.__cache_index__ = {}
        self.__lock__ = threading.Lock()
        if isinstance(self.es_server, str):
            self.es_server = self.es_server.split(',')
        self.es_client = Elasticsearch(
            self.es_server,
            http_auth=["elastic", "changeme"],
            headers={"Content-type": "application/json"}

        )

    def create_doc(self, id: str, index_name, body: dict):
        check = self.es_client.exists(index=index_name, id=id, doc_type=self.doc_type)
        if check:
            self.es_client.delete(index=index_name, id=id, doc_type=self.doc_type)
        ret = self.es_client.create(id=id, index=index_name, body=body, doc_type=self.doc_type)
        return ret

    def do_full_text_search(self, index_name, highlight, page_size, page_index, content):
        try:
            str_content = content
            __highlight = {
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"],
                "fields": {
                    "content": {}
                }
            }
            if self.configuration.config.es_max_analyzed_offset is not None:
                highlight["max_analyzed_offset"] = int(self.configuration.config.elastic_search.max_analyzed_offset)
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
                        "query": str_content
                        # "boost": 0.5

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
                        search_body_2,

                        # should_body,
                        filter_by_mark_delete

                    ]

                }
            }
            from_ = page_size * page_index
            # body = {
            #         "query": bool_body,
            #         # "_source":False,
            #         "_source":{
            #             "excludes": [ "content","meta_info","vn_on_accent_content" ]
            #
            #         },
            #
            #         "from": from_, "size": min(page_size,50)
            # }
            # if highlight:
            #     body["highlight"]=  __highlight,

            resp = None
            if highlight:
                resp = self.es_client.search(
                    index=index_name,
                    body={
                        "query": bool_body,
                        # "_source":False,
                        "_source": {
                            "excludes": ["content", "meta_info", "vn_on_accent_content"]

                        },
                        "highlight": __highlight,
                        "from": from_, "size": min(page_size, 50)})
            else:
                resp = self.es_client.search(
                    index=index_name,
                    body={
                        "query": bool_body,
                        # "_source":False,
                        "_source": {
                            "excludes": ["content", "meta_info", "vn_on_accent_content"]

                        },
                        "from": from_, "size": min(page_size, 50)})

            total_items = resp['hits']['total']['value']
            max_score = resp["hits"].get('max_score')
            ret_list = []
            highlight_contents = []
            for hit in resp['hits']['hits']:
                if hit.get("highlight") is not None:
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
                    data_item=hit["_source"].get("data_item")
                ))
            return dict(
                total_items=total_items,
                max_score=max_score,
                items=ret_list,
                text_search=content
            )
        except Exception as e:
            self.db_log.debug(index_name, e)

    def remove_doc(self, index_name, id):
        check = self.es_client.exists(index=index_name, id=id, doc_type=self.doc_type)
        if check:
            ret = self.es_client.delete(index=index_name, id=id, doc_type=self.doc_type)
            return check
        return False

    def mark_delete(self, index_name: str, id: str, mark_delete_value: bool):

        ret = self.es_client.update(
            index=index_name,
            id=id,
            doc_type=self.doc_type,
            body=dict(
                doc=dict(
                    mark_delete=mark_delete_value
                )
            )
        )
        return ret

    def update_upload_register(self, index_name, upload_register, id):
        # data_item
        check = self.es_client.exists(index=index_name, id=id, doc_type=self.doc_type)
        if check:
            ret = self.es_client.update(
                index=index_name,
                id=id,
                doc_type=self.doc_type,
                body=dict(
                    doc=dict(
                        data_item=upload_register
                    )
                )
            )
            return ret

    def create_index(self, index_name):
        if self.__cache_index__.get(index_name) is None:
            self.__lock__.acquire()
            try:
                if not self.es_client.indices.exists(index=index_name):
                    self.es_client.indices.create(
                        index=index_name,
                        body=dict(
                            settings={
                                "highlight.max_analyzed_offset": self.configuration.config.elastic_search.index_max_analyzed_offset
                            }
                        )
                    )
                else:
                    self.es_client.indices.put_settings(
                        index=index_name,
                        body=dict(
                            highlight=dict(
                                max_analyzed_offset=self.configuration.config.elastic_search.index_max_analyzed_offset
                            )
                        )
                    )
                self.__cache_index__[index_name] = index_name
            except Exception as e:
                raise e
            finally:
                self.__lock__.release()
