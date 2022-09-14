import os
import yaml


def from_file(yaml_config_path: str) -> dict:
    """
    Read yaml file even yamlfile contains utf-8 endcoding
    :param yaml_config_path:
    :return:
    """
    ret = None
    if not os.path.isfile(yaml_config_path):
        raise FileNotFoundError("'{}' was not found".format(yaml_config_path))
    with open(yaml_config_path, mode='r', encoding='utf-8') as stream:
        ret = yaml.safe_load(stream)
    if not ret:
        ret = {}
    return ret
