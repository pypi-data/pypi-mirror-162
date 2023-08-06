"""Welcome to the superwise SDK reference guide!</br>
    This page is intended to help you better understand the capabilities of our SDK.</br>
    Here you will find all information about the SDK controllers, enums and models. </br> """
import json
import logging
import os
import pkgutil

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

from superwise.config import Config, DefaultValues
from superwise.utils.client import Client
from superwise.controller.model import ModelController
from superwise.utils.storage.internal_storage.internal_storage_factory import InternalStorageFactory
from superwise.controller.version import VersionController
from superwise.controller.role import RoleController
from superwise.controller.dataentity import DataEntityController
from superwise.controller.transaction import TransactionController
from superwise.controller.segment import SegmentController
from superwise.controller.notification import NotificationController
from superwise.controller.policy import PolicyController
from superwise.controller.project import ProjectController


class Superwise:
    """ superwise class  main class for superwise package """

    def __init__(
        self,
        client_id=None,
        secret=None,
        _rest_client=None,
        email=None,
        password=None,
        _auth_url=None,
        superwise_host=None,
    ):
        """
        ### Description:

        Constructor for superwise class

        ### Args:

        `client_id`: client access token

        `secret`: secret access token

        `email`: email of user (optional)

        `password`: password of user (optional)


        """

        self.logger = logger
        if superwise_host:
            Config.SUPERWISE_HOST = superwise_host
        if _auth_url:
            Config.AUTH_URL = _auth_url
        else:
            if Config.SUPERWISE_HOST.endswith(DefaultValues.SUPERWISE_DOMAIN.value):
                # env is saas
                Config.AUTH_URL = DefaultValues.AUTH_URL
            else:
                # env is on-prem
                Config.AUTH_URL = DefaultValues.MANAGED_AUTH_URL
        client_id = client_id or os.environ.get("SUPERWISE_CLIENT_ID")
        secret = secret or os.environ.get("SUPERWISE_SECRET")
        if email and password:
            self.logger.info("login using user and password")
        elif secret is None or client_id is None:
            raise Exception("secret or email/password are mendatory fields")
        api_host = Config.SUPERWISE_HOST
        if not _rest_client:
            _rest_client = Client(client_id, secret, api_host, email, password)
        self._set_config(_rest_client)
        internal_bucket = InternalStorageFactory.get_internal_bucket(_rest_client, Config.INTERNAL_BUCKET_SETTINGS)
        self.tenant_id = _rest_client.tenant_id
        self.model = ModelController(_rest_client, self)
        self.version = VersionController(_rest_client, self)
        self.data_entity = DataEntityController(_rest_client, self)
        self.transaction = TransactionController(_rest_client, self, internal_bucket)
        self.role = RoleController(_rest_client, self)
        self.notification = NotificationController(_rest_client, self)
        self.policy = PolicyController(_rest_client, self)
        self.project = ProjectController(_rest_client, self)
        self.segment = SegmentController(_rest_client, self)

    @classmethod
    def _get_admin_settings(cls, superwise_web_client: Client):
        settings_resp = superwise_web_client.get(superwise_web_client.build_url('admin/v1/settings'))
        settings_resp.raise_for_status()

        settings = settings_resp.json()
        return settings

    @classmethod
    def _set_config(cls, superwise_web_client: Client):
        admin_settings = cls._get_admin_settings(superwise_web_client)
        Config.INTERNAL_BUCKET_SETTINGS = admin_settings.get('file_upload_settings')
