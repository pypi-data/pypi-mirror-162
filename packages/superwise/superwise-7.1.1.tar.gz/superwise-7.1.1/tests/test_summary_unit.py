import json
import os
import pathlib

import pandas as pd

from superwise.controller.summary.summary import get_summary_generator
from superwise.resources.superwise_enums import BooleanSecondaryType
from superwise.resources.superwise_enums import CategoricalSecondaryType
from superwise.resources.superwise_enums import FeatureType
from superwise.resources.superwise_enums import NumericSecondaryType
from tests import match_with_json_file

DATA_ENTITY_ASSETS_DIRECTORY = os.path.join(pathlib.Path(__file__).parent.absolute(), "resources/data_entity/assets")


def test_numeric_summary_generator():
    srs = pd.Series([i for i in range(0, 200)], name="my_numeric_feature")
    numeric_generator = get_summary_generator(FeatureType.NUMERIC.value)(srs)
    for secondary_type in NumericSecondaryType:
        f_name = os.path.join(DATA_ENTITY_ASSETS_DIRECTORY, "summary", "numeric", f"{secondary_type.name.lower()}.json")
        actual = json.loads(pd.Series(numeric_generator.generate_summary(secondary_type.value)).to_json())
        try:
            match_with_json_file(f_name, actual)
        except:
            raise Exception(f"test faild for {f_name}")


def test_categorical_summary_generator():
    print(CategoricalSecondaryType)
    for secondary_type in CategoricalSecondaryType:
        if secondary_type == CategoricalSecondaryType.CONSTANT:
            srs = pd.Series(["Category A", "Category A", "Category A"], name="my_categorical_feature")
            categorical_generator = get_summary_generator(FeatureType.CATEGORICAL.value)(srs)
        else:
            srs = pd.Series(["Category A", "Category B", "Category C"], name="my_categorical_feature")
            categorical_generator = get_summary_generator(FeatureType.CATEGORICAL.value)(srs)
        f_name = os.path.join(
            DATA_ENTITY_ASSETS_DIRECTORY, "summary", "categorical", f"{secondary_type.name.lower()}.json"
        )
        actual = json.loads(pd.Series(categorical_generator.generate_summary(secondary_type.value)).to_json())
        match_with_json_file(f_name, actual)


def test_boolean_summary_generator():
    for secondary_type in BooleanSecondaryType:
        if secondary_type == BooleanSecondaryType.FLAG:
            srs = pd.Series([True, False, None], name="my_boolean_feature").astype("category")
            srs = srs.cat.set_categories([True, False])
            boolean_generator = get_summary_generator(FeatureType.BOOLEAN.value)(srs)
        else:
            srs = pd.Series([0, 0, None], name="my_boolean_feature").astype("category")
            srs = srs.cat.set_categories([0, 1])
            boolean_generator = get_summary_generator(FeatureType.BOOLEAN.value)(srs)
        f_name = os.path.join(DATA_ENTITY_ASSETS_DIRECTORY, "summary", "boolean", f"{secondary_type.name.lower()}.json")
        actual = json.loads(pd.Series(boolean_generator.generate_summary(secondary_type.value)).to_json())
        match_with_json_file(f_name, actual)


def test_timestamp_summary_generator():
    srs = pd.Series([pd.Timestamp("01-01-2010"), pd.Timestamp("01-01-2010"), None], name="my_timestamp_feature")
    timestamp_generator = get_summary_generator(FeatureType.TIMESTAMP.value)(srs)
    f_name = os.path.join(DATA_ENTITY_ASSETS_DIRECTORY, "summary", f"timestamp.json")
    actual = timestamp_generator.generate_summary(None)
    match_with_json_file(f_name, actual)


def test_unknown_summary_generator():
    srs = pd.Series([None, None, None], name="my_unknown_feature")
    unknown_generator = get_summary_generator(FeatureType.UNKNOWN.value)(srs)
    f_name = os.path.join(DATA_ENTITY_ASSETS_DIRECTORY, "summary", f"unknown.json")
    actual = unknown_generator.generate_summary(None)
    match_with_json_file(f_name, actual)
