""" Base controller class for superwise package """
import json
import traceback
from abc import ABC
from abc import ABCMeta
from abc import abstractproperty
from urllib.parse import urlencode

from requests import Response

from superwise import logger
from superwise.utils.client import Client
from superwise.utils.exceptions import *
from superwise.models.data_entity import DataEntity
from superwise.models.model import Model
from superwise.models.notification import Notification
from superwise.models.project import Project
from superwise.models.role import Role
from superwise.models.segment import Segment
from superwise.models.transaction import Transaction
from superwise.models.validation_error import ValidationError
from superwise.models.version import Version


class BaseController(ABC):
    """Base class for controllers"""

    __metaclass__ = ABCMeta

    def __init__(self, client: Client, sw):
        """

        ### Args:

        `client`: an instance of client object

        sw`: superwise object


        """
        self.client = client
        self.path = None
        self.model_name = abstractproperty()
        self.logger = logger
        self.model = None
        self.sw = sw

    def _dict_to_model(self, params, model_name=None):
        model_name = model_name or self.model_name
        try:
            if "self" in params:
                del params["self"]
            if isinstance(params, list):
                model = list()
                for param in params:
                    cmodel = globals()[model_name](**param)
                    model.append(cmodel)
            else:
                if "__class__" in params:
                    del params["__class__"]
                model = globals()[model_name](**params)
        except Exception as err:
            traceback.print_exc()
            raise Exception("exception in create {}".format(err))
        return model

    def post(self):
        """
        ### Description:

        Prepare data and call run API POST call

        ### Return:
        requests response object
        """
        params = self.model.get_properties()
        self.logger.info("POST %s ", self.path)
        response = self.client.post(self.client.build_url(self.path), params)
        return response

    def patch(self, path=None, params=None) -> Response:
        """
        ### Description:
        Prepare data and call run API PATCH call

        ### Return:

        requests response object
        """
        path = path or self.path
        params = params or self.model.get_properties()
        self.logger.info("PATCH %s ", self.path)
        res = self.client.patch(self.client.build_url(path), params)
        return res

    def update(self, idx, params=None) -> Response:
        """
        ### Description:
        Prepare data and call run API PATCH call using a dictionary as params

        ### Return:

        requests response object
        """
        url = self.client.build_url("{}/{}".format(self.path, idx))
        params = params or self.model.get_properties()
        self.logger.info("PATCH %s ", url)
        res = self.client.patch(url, params)
        return res

    # TODO: Fix response type description in this function
    def parse_response(self, response, model_name=None, is_return_model=True):
        """
        ### Description:

        Format the response, change it from dict to be model based

        ### Args:

        `response`: response object (created by requests package)


        `model_name`: model name (dataentity, version etc)

        `is_return_model`: return model if True or response.body if False

        """
        model_name = model_name or self.model_name
        try:
            body = json.loads(response.content)
        except Exception as ex:
            raise Exception("error loading json, status code {} text {}".format(response.status_code, response.content))
        res = self._dict_to_model(body, model_name=model_name) if is_return_model else body
        return res

    def _create_update(self, model, is_return_model=True, create=True, model_name=None, **kwargs):
        """
        ### Description:

        create/update object from an instance of model

        ### Args:

        `model`: model name (dataentity, version etc)

        `is_return_model`: return model if True or response.body if False

        `create`: create if true, otherwise update


        """

        action = "create" if create else "update"
        try:
            if model.__class__.__name__ == self.model_name:
                self.model = model
                res = self.post() if create else self.patch()
            else:
                raise Exception(
                    "Model {} passed instead of {} to {}".format(
                        model.__class__.__name__, self.model_name, self.__class__.__name__
                    )
                )
            return self.parse_response(res, is_return_model=is_return_model)
        except SuperwiseValidationException:
            raise
        except Exception as e:
            traceback.print_exc()
            raise Exception("exception in {} action: {}".format(action, e))

    def create(self, model, return_model=True, **kwargs):
        """
        ### Description:

        Create object from an instance of model

        ### Args:

        `model`: model name (dataentity, version etc)

        `is_return_model`: return model if True or response.body if False

        """
        return self._create_update(model, create=True, return_model=return_model, **kwargs)

    def get_by_name(self, name):
        """"
         ### Description:

         Get entities by name, a syntactic sugar for get with name as filter

         ### Args:

         `name`: a string represent the name to filter by

         ### Return:

         a list of entities
        """
        return self.get({"name": name})

    def get(self, fields):
        """
        ### Description:

        wrapper for requests.get()

        ### Args:

        `fields`:  optinal fields for filtering

        ### Return:

        parsed data (dict) from backend
        """
        uri = self.client.build_url(self.path)

        fields_formatted = urlencode(fields)
        uri = "{}?{}".format(uri, fields_formatted)
        self.logger.info("GET with fields %s ", uri)
        res = self.client.get(uri)
        return self.parse_response(res)

    def get_by_id(self, idx):
        """
        ### Description:

        Get a specific resource by id

        ### Args:
        `idx`:  id of entity to fetch

        ### Return:

        parsed model data (dict) from backend
        """

        url = self.client.build_url("{}/{}".format(self.path, idx))
        self.logger.info("GET  %s ", url)
        res = self.client.get(url)
        return self.parse_response(res)

    def delete(self, model):
        """
        ### Description:

        Delete an object

        ### Args:

        `model`:  a Superwise.Models object

        ### Return:

        parsed response from server (dict)
        """
        if not model.id:
            raise SuperwiseException("Delete allowed only to model exist in server, this is probably a new model")
        return self.delete_by_id(model.id)

    def delete_by_id(self, idx):
        """
        ### Description:

        Delete an object by a given id

        ### Args:

        `idx`:  id to delete

        ### Return:

        parsed response from server (dict)
        """
        url = self.client.build_url("{}/{}".format(self.path, idx))
        self.logger.info("DELETE  %s ", url)
        res = self.client.delete(url)
        return res

    def __str__(self):
        properties = self.model.get_properties()
        return f"<Superwise.{self.__class__.__name__} " f"{properties}"
