""" This module implement Project model  """
import datetime

from superwise.models.base import BaseModel


class Project(BaseModel):
    """ Project model class """

    def __init__(
        self,
        id: int = None,
        name: str = None,
        description: str = None,
        created_at: datetime.datetime = None,
        created_by: str = None,
        **kwargs
    ):
        """
        ### Description:

        Constructor for Model class

        ### Args:

        `id`: id of project

        `name`: name of project

        `description`: description for the project

        `created_at`: date of creation

        created_by: user who created the project
        """
        self.id = id
        self.name = name
        self.description = description
        self.created_at = created_at
        self.created_by = created_by
