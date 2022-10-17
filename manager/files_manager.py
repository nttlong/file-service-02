import es_connection
import db_connection
import api_models.Model_Files


def search_content_of_file(app_name: str, content: str):
    """
    Thực hiện tìm kiếm ter6n nội dung của file
    :param app_name: app
    :param content: nội dung
    :return:
    """
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
                search_body

            ]
        }
    }
    prefix_app = {
        "prefix": {
            "path.virtual": f'\\{app_name}\\'
        }
    }
    bool_body = {
        "bool": {
            "must": [
                prefix_app,
                should_body
            ]

        }
    }
    resp = es_connection.es_client.search_engine(index=es_connection.es_index, query=bool_body, highlight=highlight)
    total_items = resp['hits']['total']['value']
    max_score = resp["hits"].get('max_score')
    ret_list = []
    for hit in resp['hits']['hits']:
        highlight_contents = hit["highlight"].get('content', [])
        res_content = hit["_source"].get('content')
        score = hit.get("score")
        file_name = hit["_source"]["file"]["filename"]
        ret_list.append(dict(
            highlight=highlight_contents,
            content=res_content,
            score=score,
            server_file_id=file_name  # Tên file
        ))
    return dict(
        total_items=total_items,
        max_score=max_score,
        items=ret_list,
        text_search=content
    )


def search_content_of_file_and_map_upload(app_name: str, content: str):
    """
    Thực hiện tìm kiếm trên ES và map với mongo database
    :param app_name:
    :param content:
    :return:
    """
    db = db_connection.connection.get_database(app_name)
    upload_docs = api_models.Model_Files.DocUploadRegister(db)
    """
    Tạo một python mongodb doc tương ứng với 'DocUploadRegister collection'
    """
    search_result = search_content_of_file(app_name, content)  # Tìm trên Elastic Search

    def get_list():
        for x in search_result["items"]:
            upload_id = x["server_file_id"].split('.')[0]  # tách lấy id upload
            upload_doc_item = upload_docs.find_one(upload_docs._id == upload_id)
            ret_dict = dict(
                search_item=x,
                doc_item=upload_doc_item
            )
            yield ret_dict

    return dict(
        total_items=search_result["total_items"],
        max_score=search_result["max_score"],
        items=get_list(),
        text_search=search_result["text_search"]
    )
