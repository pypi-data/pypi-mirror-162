""" This module implement roles functionality  """
from superwise.controller.base import BaseController
from superwise.models.model import Model


class RoleController(BaseController):
    """ Role controller class, implement functionalities for roles API """

    def __init__(self, client, sw):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise object

        """

        super().__init__(client, sw)
        self.path = "model/v1/roles"
        self.model_name = "Role"

    def list_to_dict(self, model_list):
        """
        ### Description:

        convert a list of models into dict

        ### Args:

        `model_list`: list of models

        ### Return:

         Dict of RoleModel()
        """

        dict = {}
        for model in model_list:
            properties = model.get_properties()
            dict[properties["description"]] = properties
        return dict
