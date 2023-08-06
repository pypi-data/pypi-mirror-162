""" This module implement tasks functionality  """
from superwise.controller.base import BaseController
from superwise.models.model import Model
from superwise.models.project import Project


class ModelController(BaseController):
    """Class ModelController - responsible for task functionality"""

    def __init__(self, client, sw):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise  object

        """
        super().__init__(client, sw)
        self.path = "admin/v1/models"
        self.model_name = "Model"

    def archive(self, model):
        """

        ### Args:

        `model`: model object to archive

        ### Return:

        response object
        """
        res = self.update(model.id, params={"is_archived": True})
        return res
