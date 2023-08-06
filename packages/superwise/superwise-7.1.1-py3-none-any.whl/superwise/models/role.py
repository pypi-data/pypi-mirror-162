""" This module implement Role model  """
from superwise.models.base import BaseModel


class Role(BaseModel):
    """ Role model class, model  for roles data """

    def __init__(
        self,
        id=None,
        model_type_id=None,
        is_nullable=None,
        description=None,
        internal_name=None,
        is_label=None,
        is_optional=None,
        role=None,
        value=None,
        **kwargs
    ):
        """
        ### Description:

        Constructor of Role class

        ### Args:

        `id`: id of role (int)

        `model_type_id`: model type id (ModelType enum value)

        `is_nullable`:

        `description`: description of the role

         internal_name`:

        `is_label`:

        `is_optional`:

        `role`:

        `value`:

        """
        self.model_type_id = model_type_id
        self.description = description
        self.internal_name = internal_name
        self.is_label = is_label
        self.is_optional = is_optional
        self.value = value
        self.is_nullable = is_nullable
        self.role = role
        self.id = id
