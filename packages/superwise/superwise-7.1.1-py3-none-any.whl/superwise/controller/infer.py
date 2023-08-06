""" This module implement infer dtypes functionality  """
import numpy as np
import pandas as pd


def infer_dtype(df):
    """
    ### Description:

     This function infer dtypes of a given df

    ### Args:

    `df`: a pandas df of baseline/data


    ### Return:

    dictionary <feature_name:dtype_string>
    """
    df.columns = df.columns.str.lower()
    res = df.apply(_infer_entity_type)
    return res.to_dict()


def _infer_entity_type(feature):
    """
    ### Description:

     Infer an entity type (dtype)

    ### Args:

    `feature`:  pandas series of a feature


    ### Return:

    string represent the type of entity
    """

    """
    Infer an entity type (dtype)
    :param feature: feature pandas series
    """
    nunique = feature.nunique()
    values = feature.dropna()
    if nunique == 0:
        return "Unknown"
    if np.issubdtype(feature.dtype, np.bool_) or (
        (np.issubdtype(feature.dtype, np.number) and values.isin([1, 0]).all())
    ):
        return "Boolean"
    if np.issubdtype(feature.dtype, np.number):
        return "Numeric"
    if np.issubdtype(feature.dtype, np.datetime64):
        return "Timestamp"
    if np.issubdtype(pd.to_datetime(feature, errors="ignore").dtype, np.datetime64):
        return "Timestamp"
    if values.apply(np.isscalar).all():
        return "Categorical"
    return "Unknown"
