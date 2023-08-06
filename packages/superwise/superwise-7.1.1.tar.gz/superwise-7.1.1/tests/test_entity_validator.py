import os

import numpy as np
import pandas as pd
import pytest

from superwise.controller.summary.entities_validator import EntitiesValidationError
from superwise.controller.summary.entities_validator import EntitiesValidator
from tests.resources.data_entity import DATA_ENTITY_ASSETS_DIRECTORY


@pytest.fixture(scope="function")
def basic_baseline_and_schema():
    basic_baseline = pd.read_json(
        os.path.join(DATA_ENTITY_ASSETS_DIRECTORY, "baseline", "basic_baseline.json"), convert_dates=["label_ts", "ts"]
    )
    basic_schema = pd.read_json(os.path.join(DATA_ENTITY_ASSETS_DIRECTORY, "baseline", "basic_schema.json"))
    yield basic_baseline, basic_schema


def test_schema_has_not_reserved_names(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["model_id"] = "my task id"
    baseline["version_id"] = "my version id"
    schema = schema.append(
        dict(dimension_start_ts=None, name="model_id", role="feature", type="Categorical"), ignore_index=True
    )
    schema = schema.append(
        dict(dimension_start_ts=None, name="version_id", role="feature", type="Categorical"), ignore_index=True
    )
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "contains reserved words" in validation_error.value.reason


def test_column_names_match_schema(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    schema["name"] = schema["name"].str.upper()
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "columns exist in data but are missing" in validation_error.value.reason


def test_has_all_required_roles(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    a_baseline, a_schema = baseline.drop("record_id", axis=1), schema[schema["role"] != "id"]
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(a_schema, a_baseline).prepare()
    assert "columns exist in required roles but are missing from existing roles" in validation_error.value.reason


def test_is_valid_dimension_count(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    schema["dimension_start_ts"] = "2020-01-01 00:00:00"
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "Maximum allowed dimensions is 10" in validation_error.value.reason


def test_is_valid_dimension(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    schema.loc[schema["name"] == "prediction_probability", "dimension_start_ts"] = "2020:01:01 00:00:00"
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "type Categorical is required" in validation_error.value.reason


def test_time_stamp_types_valid(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["ts"] = "yesterday"
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "Column ts - marked as type Timestamp but is malformed" in validation_error.value.reason


def test_boolean_types_valid(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["boolean_flag"] = baseline["boolean_flag"].map({True: "Elvis", False: "Presley"})
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "Column boolean_flag - boolean column must be" in validation_error.value.reason


def test_is_valid_record_id(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["record_id"] = 1
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "duplicated values" in validation_error.value.reason


def test_is_valid_prediction_probability(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["prediction_probability"] = baseline["prediction_probability"] * 100
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "0 to 1 is expected" in validation_error.value.reason


def test_is_valid_label_ts(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline.loc[0, "label_ts"] = pd.NaT
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "has null values" in validation_error.value.reason


def test_is_valid_prediction_ts(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline.loc[0, "ts"] = pd.NaT
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "has null values" in validation_error.value.reason


def test_is_valid_label_weight(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    schema = schema.append(
        dict(dimension_start_ts=None, name="label_weight", role="label weight", type="Categorical"), ignore_index=True
    )
    baseline["label_weight"] = "One"
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "type Numeric is required" in validation_error.value.reason


def test_happy_flow(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    EntitiesValidator(schema, baseline).prepare()


def test_empty_boolean(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["boolean_flag"] = None
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "has all null values" in validation_error.value.reason


def test_empty_categorical(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["country"] = None
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "has all null values" in validation_error.value.reason


def test_empty_numeric(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["age"] = None
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "has all null values" in validation_error.value.reason


def test_empty_ts(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["last_reviewed"] = None
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "has all null values" in validation_error.value.reason


def test_regression(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    schema.loc[schema["name"].isin(["label", "prediction_value"]), "type"] = "Numeric"
    schema = schema[schema["name"] != "prediction_probability"]
    baseline = baseline.drop("prediction_probability", axis=1)
    baseline["prediction_value"] = np.random.rand(len(baseline))
    baseline["label"] = baseline["prediction_value"]
    EntitiesValidator(schema, baseline).prepare()


def test_inf_is_invalid(basic_baseline_and_schema):
    baseline, schema = basic_baseline_and_schema
    baseline["age"] = np.inf
    with pytest.raises(EntitiesValidationError) as validation_error:
        EntitiesValidator(schema, baseline).prepare()
    assert "Column age - (numeric) has 3 records with inf/-inf values" in validation_error.value.reason
