from __future__ import absolute_import, division, print_function, unicode_literals
from past.builtins import basestring

import os.path
import ruamel
from publisher.processing.data_sources.utils import remove_whitespace_from_string

from publisher.exceptions import ContentMissingError
from publisher.processing.data_sources.utils import YamlObject
import publisher.settings as settings


def remove_whitespace(data):
    if isinstance(data, ruamel.yaml.comments.CommentedSeq):
        for value in data:
            remove_whitespace(value)
    elif isinstance(data, ruamel.yaml.comments.CommentedMap):
        for key, value in data.items():
            if isinstance(value, basestring):
                data[key] = remove_whitespace_from_string(data[key])
            elif isinstance(value, (ruamel.yaml.comments.CommentedMap,
                                    ruamel.yaml.comments.CommentedSeq)):
                remove_whitespace(value)

    return data


def get_more_info_data(info_id, code):
    yaml_dir = os.path.join(settings.PROCEDURE_CHECKOUT_DIRECTORY, code, "build_assets", "moreInfo", info_id)

    yaml_file = os.path.join(yaml_dir, info_id + ".yml")
    source_asset_dir = os.path.join(yaml_dir, "assets")

    if not os.path.isfile(yaml_file):
        raise ContentMissingError("Yaml infocard not found in {0}".format(yaml_file))

    print("-- Found more info card: %s --" % info_id)
    return read_yaml_data(yaml_file), source_asset_dir


def read_yaml_data(yaml_file):
    yaml = YamlObject()

    with open(yaml_file, "r") as f:
        data = yaml.load(f)
        return remove_whitespace(data)
