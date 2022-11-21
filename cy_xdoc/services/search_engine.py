import elasticsearch

import cy_es
import cy_xdoc.configs
class SearchEngine:
    def __init__(self):
        self.config = cy_xdoc.configs.config
        self.client=elasticsearch.Elasticsearch(
            cy_xdoc.configs.config.elastic_search.server
        )
        self.prefix_index = cy_xdoc.configs.config.elastic_search.prefix_index

    def get_index(self,app_name):
        return f"{self.prefix_index}_{app_name}"
    def delete_doc(self, app_name, upload_id):
        raise NotImplemented

    def mark_delete(self, app_name, id, mark_delete_value):
        raise NotImplemented

    def full_text_search(self, app_name, content, page_size:int, page_index:int, highlight:bool):
        search_expr = (cy_es.buiders.mark_delete==False) & cy_es.match_phrase(
            field=cy_es.buiders.content,
            content=content

        )
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
            index= self.get_index(app_name),
            highlight= highlight_expr,
            filter=search_expr
        )
        return ret