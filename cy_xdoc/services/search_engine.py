import elasticsearch
import cy_kit
import cy_es
import cy_xdoc.configs


class SearchEngine:
    def __init__(self):
        self.config = cy_xdoc.configs.config
        self.client = elasticsearch.Elasticsearch(
            cy_xdoc.configs.config.elastic_search.server
        )
        self.prefix_index = cy_xdoc.configs.config.elastic_search.prefix_index

    def get_index(self, app_name):
        if app_name == "admin":
            app_name = self.config.admin_db_name
        return f"{self.prefix_index}_{app_name}"

    def delete_doc(self, app_name, id: str):
        return cy_es.delete_doc(
            client=self.client,
            index= self.get_index(app_name),
            id =id
        )


    def mark_delete(self, app_name, id, mark_delete_value):
        raise NotImplemented

    def full_text_search(self, app_name, content, page_size: int, page_index: int, highlight: bool):
        search_expr = (cy_es.buiders.mark_delete == False) & cy_es.match(
            field=cy_es.buiders.content,
            content=content

        )
        skip = page_index * page_size
        highlight_expr = None
        if highlight:
            highlight_expr = cy_es.buiders.content
        ret = cy_es.search(
            client=self.client,
            limit=page_size,
            excludes=[
                cy_es.buiders.content,
                cy_es.buiders.meta_info,
                cy_es.buiders.vn_on_accent_content],
            index=self.get_index(app_name),
            highlight=highlight_expr,
            filter=search_expr,
            skip=skip

        )
        return ret

    def get_doc(self, app_name: str, id: str, doc_type: str = "_doc"):
        return cy_es.get_doc(client=self.client, id=id, doc_type=doc_type, index=self.get_index(app_name))

    def copy(self, app_name: str, from_id: str, to_id: str, attach_data, run_in_thread: bool = True):
        @cy_kit.thread_makeup()
        def copy_elastics_search(app_name: str, from_id: str, to_id: str, attach_data):
            es_doc = self.get_doc(id=from_id, app_name=app_name)
            if es_doc:
                es_doc.source.upload_id = to_id
                es_doc.source.data_item = attach_data
                self.create_doc(app_name=app_name, id=to_id, body=es_doc.source)

        if run_in_thread:
            copy_elastics_search(app_name,  from_id,to_id, attach_data).start()
        else:
            copy_elastics_search(app_name,  from_id,to_id, attach_data).start().join()

    def create_doc(self, app_name, id:str, body):
        return cy_es.create_doc(
            client=self.client,
            index=self.get_index(app_name),
            id=id,
            body=body
        )
