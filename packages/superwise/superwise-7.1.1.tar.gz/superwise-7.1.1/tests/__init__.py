import json
import os.path
import pathlib
from pprint import pprint

from superwise import Superwise
from superwise.models.data_entity import DataEntity
from tests.conf.config import config


def get_sw():
    """
    Get instance of superwise object for testing

    :return: superwise object
    """
    sw = Superwise(client_id=config["CLIENT_ID"], secret=config["SECRET"])
    return sw


def print_results(title, obj):
    print("####### {} #######".format(title))
    pprint(obj)
    print("\n")


def get_entities_fixture():
    with open("tests/resources/basic_schema.json", "r") as fh:
        schema = json.loads(fh.read())

    entities = [
        DataEntity(
            name=m["name"], type=m["type"], is_dimension=m["is_dimension"], role=m["role"], feature_importance=None
        )
        for m in schema
    ]
    return entities


COMMON_ASSETS_DIRECTORY = os.path.join(pathlib.Path(__file__).parent.absolute(), "common_assets")


def match_with_json_file(path, obj):
    with open(path, "r") as f:
        expected_result = json.load(f)
    assert expected_result == obj
