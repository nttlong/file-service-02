import pathlib
import sys

sys.path.append(
    pathlib.Path(__file__).parent.__str__()
)
from elasticsearch import Elasticsearch
import typing
import cy_es_x

DocumentFields = cy_es_x.DocumentFields
buiders = cy_es_x.docs


def search(client: Elasticsearch,
           index: str, filter,
           excludes: typing.List[DocumentFields] = [],
           skip: int = 0,
           limit: int = 50,
           highlight: DocumentFields = None):
    return cy_es_x.search(
        client=client,
        index=index,
        excludes=excludes,
        skip=skip,
        limit=limit,
        highlight=highlight,
        filter=filter
    )


def get_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:
    return cy_es_x.get_doc(client, index, id, doc_type=doc_type)


def create_doc(client: Elasticsearch, index: str, id: str, body,
               doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:
    return cy_es_x.create_doc(
        client=client,
        index=index,
        doc_type=doc_type,
        data=body,
        id=id
    )


match_phrase = cy_es_x.match_phrase
match = cy_es_x.match
