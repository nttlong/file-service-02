import pathlib
import sys

import cy_es

sys.path.append(
    pathlib.Path(__file__).parent.__str__()
)
from elasticsearch import Elasticsearch
import typing
import cy_es_x

DocumentFields = cy_es_x.DocumentFields
buiders = cy_es_x.docs

def create_index(client:Elasticsearch,index:str,body=None):
    return cy_es_x.create_index(
        index==index,
        body=body,
        client=client
    )
def search(client: Elasticsearch,
           index: str, filter,
           excludes: typing.List[DocumentFields] = [],
           skip: int = 0,
           limit: int = 50,
           highlight: DocumentFields = None,
           sort=None):
    return cy_es_x.search(
        client=client,
        index=index,
        excludes=excludes,
        skip=skip,
        limit=limit,
        highlight=highlight,
        filter=filter,
        sort = sort
    )


def get_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:
    return cy_es_x.get_doc(client, index, id, doc_type=doc_type)

def delete_doc(client: Elasticsearch, index: str, id: str, doc_type: str = "_doc"):

    return cy_es_x.delete_doc(client=client,index=index,id=id,doc_type=doc_type)
def create_doc(client: Elasticsearch, index: str, id: str, body,
               doc_type: str = "_doc") -> cy_es_x.ESDocumentObjectInfo:

    return cy_es_x.create_doc(
        client=client,
        index=index,
        doc_type=doc_type,
        body=body,
        id=id
    )


match_phrase = cy_es_x.match_phrase
match = cy_es_x.match


def update_doc_by_id(client: Elasticsearch, index: str, id: str, data, doc_type: str = "_doc"):
    return cy_es_x.update_doc_by_id(
        client=client,
        index=index,
        id=id,
        data=data,
        doc_type=doc_type
    )


def nested(field_name:str, filter:dict):
    return cy_es_x.nested(prefix=field_name,filter=filter)


def create_filter_from_dict(filter:dict):
    return cy_es_x.create_filter_from_dict(filter)


def is_exist(client:Elasticsearch, index:str, id:str,doc_type:str ="_doc")->bool:
    return cy_es_x.is_exist(
        client=client,
        index=index,
        id=id,
        doc_type=doc_type
    )


def get_docs(client:Elasticsearch, index:str, doc_type:str ="_doc"):
    return cy_es_x.get_docs(
        client=client,
        index = index,
        doc_type = doc_type
    )


def create_mapping(fields:typing.List[cy_es_x.DocumentFields]):
    return cy_es_x.create_mapping(fields)


def set_norms(field:cy_es.buiders, field_type:str, enable:bool):
    return cy_es_x.set_norms(
        field=field,
        enable=enable,
        field_type =field_type
    )


def put_mapping(client: Elasticsearch, index: str, body):
    ret = cy_es_x.put_mapping(
        client=client,
        index=index,
        body=body
    )
    client.indices.refresh(index = index)