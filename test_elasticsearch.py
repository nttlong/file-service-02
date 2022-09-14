from  manager import files_manager
ret = files_manager.search_content_of_file_and_map_upload("hps-file-test","quyết định bộ trường")
for x in ret["items"]:
    print(x["doc_item"])