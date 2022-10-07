import json
import logging
import sys


def get_arg(key:str, default_value=None):
    for x in sys.argv:
        if key+'=' in x:
            val = x.split('=')[1]
            return val
    return default_value


def get_arg_and_decode_to_dict(key, share_key):
    from jose import jwt
    data = get_arg(key)
    txt_data = jwt.decode(
        data,
        share_key,
        algorithms=['HS256']

    )

    return txt_data

class ArgConfig:
    def __int__(self):
        self.share_key=None
        self.db_config:dict=None
        self.msg_folder=None
        self.fs_crawler_path=None
        self.tmp_upload_folder=None


def get_config()->ArgConfig:
    ret = ArgConfig()

    ret.share_key = get_arg('share-key', None)
    ret.db_config = get_arg_and_decode_to_dict('db-config', ret.share_key)
    ret.msg_folder = get_arg('msg-folder', "./tmp/msg")
    ret.fs_crawler_path = get_arg('fs-path')
    ret.tmp_upload_folder=get_arg('tmp-upload-folder')
    return ret
