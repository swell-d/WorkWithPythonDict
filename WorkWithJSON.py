import codecs
import json
import os
import pathlib

import GlobalFunctions


def load_dict_from_json(file_name):
    if os.path.exists(file_name):
        with codecs.open(file_name, 'r', 'utf-8') as file:
            return json.loads(file.read())
    GlobalFunctions.print(f'load_dict_from_json: {file_name} not found. empty dictionary returned')
    return {}


def save_dict_to_json(dictionary, file_name):
    if '\\' in file_name: pathlib.Path(file_name[:file_name.rfind('\\')]).mkdir(parents=True, exist_ok=True)
    with codecs.open(file_name, 'w', 'utf-8') as file:
        file.write(json.dumps(dictionary))
