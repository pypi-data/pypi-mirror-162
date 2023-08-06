""" This module implement Model model  """
import warnings

from superwise.models.base import BaseModel


class Model(BaseModel):
    """ Model model class """

    def __init__(
        self,
        id=None,
        project_id=None,
        external_id=None,
        name=None,
        description=None,
        monitor_delay=None,
        time_units=None,
        is_archived=None,
        active_version_id=None,
        **kwargs
    ):
        """
        ### Description:

        Constructor for Model class

        ### Args:

        `id`: id of model

        `project_id`: id of project

        `external_id`: external/secondary identifier, use it to map between your id and superwise

        `name`: name of model

        `description`: description for the model

        `time_units`:

        `is_archive`:
        """
        self.external_id = external_id
        self.project_id = project_id
        self.name = name
        self.id = id or None
        self.description = description
        if monitor_delay is not None:
            warnings.warn("Passing monitor_delay is deprecated, it should be configured for a specific Policy")
        self.time_units = time_units
        self.is_archived = is_archived
        self.active_version_id = active_version_id
