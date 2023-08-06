""" This module implement tasks functionality  """

from superwise.controller.base import BaseController


class ProjectController(BaseController):
    """Class ProjectController - responsible for task functionality"""

    def __init__(self, client, sw):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise  object

        """
        super().__init__(client, sw)
        self.path = "model/v1/projects"
        self.model_name = "Project"
