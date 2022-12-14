import fastapi
import cy_xdoc.services.search_engine
import cy_kit
import cy_web
import cy_xdoc.auths
from typing import Optional
@cy_web.hanlder("post","{app_name}/search")
def file_search(app_name: str, content: Optional[str],
                      page_size: Optional[int],
                      page_index: Optional[int],
                      highlight: Optional[bool],
                      privileges: Optional[dict],
                      token = fastapi.Depends(cy_xdoc.auths.Authenticate)):
    """
    <br/>
    <p>
    <b>For a certain pair of Application and  Access Token </b><br/>
    This API allow thou search content in full content of any document.<br>
    <code>\n
        {
            content:<any text for searching>,
            page_size: <limit search result>,
            page_index: <page index of result, start value is 0>,
            highlight: <Highlight match content if set true>,
            privileges: <JSON filter>

        }
    </code>
    <p >
        <b style='color:red !important'> Highlight maybe crash Elasticsearch or ake very long time </b>
    <p>
    <h1>
     How to make privileges filter json expression?
    </h1>
    <div>
        Privileges filter json expression has some bellow key words (they are nested together):
        <ol>
            <li><b>$and</b>: and logical follow by list of other filters.</li>
            <li><b>$or</b>: or logical follow by list of other filters.</li>
            <li><b>$not</b>: negative a filter expression.</li>
            <li><b>$contains</b>: check a privileges has contains a list of values.</li>
        </ol>
    </div>
    <code>\n
        docs = [
                 {
                    id:1,
                    users:['admin','root'],
                    position: ['staff','deputy']
                 } ,
                 {
                    id:2,
                    users :['root','admin','user1'],
                    position: ['director','deputy']
                 }
                ]
        //Example filter all document share to user root and admin only
        filter ={
                    users:['root','admin']
                }
        thou will get docs=[{id:1}]

        //filter all document has share root and admin
        filter ={
                    users:{
                        $contains:['root','admin']
                    }

                }
        //filter all document share to director position but deputy
        filter = {
                    $and:[
                        {
                            position:{
                                $contains:['director']
                            },
                            {
                                $not: {
                                    position:{
                                        $contains:['deputy']
                                    }
                                }
                            }
                        }
                    ]
                }

    </code>

    </p>
    :param privileges: <p> Filter by privileges<br/> The privileges tags is a pair key and values </p>
    :param request:
    :param app_name:
    :param content:
    :param page_size:
    :param page_index:
    :param token:
    :return:
    """
    if highlight is None:
        highlight=False
    search_services:cy_xdoc.services.search_engine.SearchEngine = cy_kit.singleton(cy_xdoc.services.search_engine.SearchEngine)
    # search_result = search_content_of_file(app_name, content, page_size, page_index)
    search_result=search_services.full_text_search(
        app_name=app_name,
        content =content,
        page_size=page_size,
        page_index=page_index,
        highlight=highlight,
        privileges= privileges
    )

    ret_items = []
    url = cy_web.get_host_url()+"/api"
    for x in search_result.items:
        upload_doc_item = x._source.data_item
        if upload_doc_item:
            # upload_doc_item.UploadId = upload_doc_item._id
            upload_doc_item.Highlight = x.highlight
            upload_doc_item.UrlOfServerPath= f"{url}/{app_name}/file/{upload_doc_item.FullFileName}"
            upload_doc_item.AppName = app_name
            upload_doc_item.RelUrlOfServerPath = f"/{app_name}/file/{upload_doc_item.FullFileName}"
            upload_doc_item.ThumbUrl = url + f"/{app_name}/thumb/{upload_doc_item['_id']}/{upload_doc_item.FileName}.png"
            ret_items += [upload_doc_item]

    return dict(
        total_items=search_result.hits.total,
        max_score=search_result.hits.max_score,
        items=ret_items,
        text_search=content
    )
