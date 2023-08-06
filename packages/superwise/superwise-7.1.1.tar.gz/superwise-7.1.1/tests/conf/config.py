import json
import os
import pkgutil

try:
    config = json.loads(pkgutil.get_data("tests", "/conf/config.json"))
except Exception as ex:
    config = json.loads(pkgutil.get_data("tests", "/conf/config.example.json"))
