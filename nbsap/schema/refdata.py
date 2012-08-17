import os
import json

from collections import OrderedDict

def _load_json(name):
    with open(os.path.join(os.path.dirname(__file__), name), "rb") as f:
        return json.load(f)

def _sorter(value):
    _lang_order = ['en', 'fr', 'nl']
    return _lang_order.index(value[0])

language = OrderedDict(sorted(_load_json("../refdata/languages.json").items(), key=_sorter))
