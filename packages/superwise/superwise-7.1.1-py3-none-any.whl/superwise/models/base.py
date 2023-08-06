""" This module contain BaseModel class  """
import datetime
from enum import Enum

import pandas as pd


class BaseModel:
    """ Base model """

    def __init__(self, **kwargs):
        """
         ### Description:

         Constructor of BaseModel class

         """
        self.id = kwargs.get("id")

    def from_datetime(self, date):
        """
         ### Description:

         Convert datetime helper

         ### Args:

         `date`: a datetime.datetime object

        ### Return:

        string of date in iso format
        """

        if pd.isna(date):
            return None
        elif isinstance(date, datetime.datetime):
            return date.isoformat()
        else:
            return date

    def get_properties(self):
        """
        ### Description:

        Get properties of model as a dictionary

        ### Args:

        `date`: a datetime.datetime object

        ### Return:

        dictionary of model properties
        """
        return dict(
            (name, getattr(self, name))
            for name in dir(self)
            if not name.startswith("__") and not callable(getattr(self, name))
        )

    def __repr__(self):
        properties = self.get_properties()
        prop_str = ""
        for p in properties:
            prop_str += f"\t{p}: {properties[p]}\n"
        return f"<Superwise.models.{self.__class__.__name__} object> " f"{{\n" f"{prop_str}" f"}}"
