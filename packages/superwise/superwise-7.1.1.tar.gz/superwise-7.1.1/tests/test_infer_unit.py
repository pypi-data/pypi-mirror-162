import pandas as pd

from superwise.controller.infer import _infer_entity_type
from superwise.controller.infer import infer_dtype


def test_infer_bool():
    srs = pd.Series([False, True], name="bool_feature")
    dtype = _infer_entity_type(srs)
    assert dtype == "Boolean"


def test_infer_numeric():
    srs = pd.Series([1, 2, 3, 4, 1000])
    dtype = _infer_entity_type(srs)
    assert dtype == "Numeric"


def test_infer_categorical():
    srs = pd.Series(["abc", "abcd", "abc", "adsfasfdasdf"])
    dtype = _infer_entity_type(srs)
    assert dtype == "Categorical"

    srs = pd.Series(["abc", 12, 12312312312, 1231231231, 12, 12, 12, 12])
    dtype = _infer_entity_type(srs)
    assert dtype == "Categorical"


def test_infer_unknown_empty_series():
    srs = pd.Series([])
    dtype = _infer_entity_type(srs)
    assert dtype == "Unknown"


def test_infer_unknown_series():
    srs = pd.Series([None, None, None])
    dtype = _infer_entity_type(srs)
    assert dtype == "Unknown"


def test_infer_timestamp_pd_timestamp():
    srs = pd.Series([pd.Timestamp("01-01-2010"), pd.Timestamp("01-01-2011")])
    dtype = _infer_entity_type(srs)
    assert dtype == "Timestamp"


def test_infer_timestamp_from_str():
    srs = pd.Series(["01-01-2010", "01-01-2011"])
    dtype = _infer_entity_type(srs)
    assert dtype == "Timestamp"

    srs = pd.Series(["01-01-2010 12:12", "01-01-2011 11:11"])
    dtype = _infer_entity_type(srs)
    assert dtype == "Timestamp"


def test_infer_dtype():
    df = pd.DataFrame({"f_bool": [True, False, True], "f_cat": ["Linux", "Win", "IOS"]})
    ret = infer_dtype(df)
    assert ret == {"f_bool": "Boolean", "f_cat": "Categorical"}
