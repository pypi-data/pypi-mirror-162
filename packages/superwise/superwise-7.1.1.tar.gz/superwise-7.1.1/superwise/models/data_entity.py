""" This module implement DataEntity model  """
import json

import pandas as pd

from superwise.models.base import BaseModel
from superwise.resources.superwise_enums import get_enum_value


class DataEntity(BaseModel):
    """ data entity model class """

    def __init__(
        self,
        id=None,
        dimension_start_ts=None,
        type=None,
        name=None,
        role=None,
        feature_importance=None,
        summary=None,
        secondary_type=None,
        data_type=None,
        **kwargs
    ):
        """
        ### Description:

        Constructor for DataEntity class

        ### Args:

        `id`: id if dataentity

        `dimension_start_ts`:

        `type`:

        `name`:

        `is_dimension`:

        `role`:

        `feature_importance`:

        `summary`: dictionary of summarised data

        `secondary_type`:

        `data_type`:
        """

        self.name = name.lower() if name else None
        self.type = get_enum_value(type)
        self.role = get_enum_value(role)
        self.feature_importance = feature_importance
        self.summary = summary
        self.secondary_type = secondary_type
        self.id = id
        self.dimension_start_ts = self.from_datetime(dimension_start_ts)
        self.data_type = data_type

    @staticmethod
    def list_to_df(data_entities):
        """
        ### Description:

        Get list of DataEntity objects and return them as pandas dataframe

        ### Args:

        `data_entities`: List[DataEntity] - list of DataEntity objects

        ### Return:

        pandas df of data entities
         """

        data = [d.get_properties() for d in data_entities]
        df = pd.DataFrame(data)
        return df

    @staticmethod
    def df_to_list(data_entities_df):
        """
        ### Description:

        Get data entities dataframe and return list of DataEntity objects

        ### Args:

        `data_entities_df`: pandas df of data entities

        ### Return:

        List[DataEntity] - list of DataEntity objects
         """

        data = json.loads(data_entities_df.to_json(orient="records"))
        entities = []
        [entities.append(DataEntity(**d)) for d in data]
        return entities


class DataEntitySummary(BaseModel):
    """ summary model class """

    def __init__(self, idx=None, summary=None):
        """
        ### Description:

        Constructer for DataEntitySummary class

        ### Args:

        `idx`: id of dataEntity

        `summary`: summary of dataentity (dict)
        """

        self.id = idx
        self.summary = summary
