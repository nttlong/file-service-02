import json
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
