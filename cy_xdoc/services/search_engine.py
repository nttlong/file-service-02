class SearchEngine:

    def delete_doc(self, app_name, upload_id):
        raise NotImplemented

    def mark_delete(self, app_name, id, mark_delete_value):
        raise NotImplemented

    def full_text_search(self, app_name, content, page_size, page_index, highlight):
        raise NotImplemented