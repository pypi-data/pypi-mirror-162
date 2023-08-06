import abc
import logging
import uuid
from enum import Enum

from superwise.utils.client import Client
from superwise.utils.exceptions import SuperWiseValidationError

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class CloudProvider(Enum):
    GCP = 'GCP'
    AZURE = 'AZURE'


class InternalStorage(abc.ABC):
    @staticmethod
    def generate_file_name(extension: str, prefix: str = None):
        file_prefix = ''
        if prefix:
            file_prefix = f'{prefix}_'
        return f"{file_prefix}{uuid.uuid4()}{extension}"

    def __init__(self, superwise_web_client: Client):
        self._superwise_web_client = superwise_web_client
        self._cloud_token = None

    def _refresh_cloud_token(self):
        resp = self._superwise_web_client.get(self._superwise_web_client.build_url('admin/v1/settings/jwt-token'))
        resp.raise_for_status()
        self._cloud_token = resp.json()

    @abc.abstractmethod
    def _is_cloud_token_active(self) -> bool:
        pass

    @abc.abstractmethod
    def _put_in_storage(self, blob_name: str, content: str):
        pass

    def upload(self, blob_path: str, content: str):
        """

        ### Description:

        Upload a file's content to Superwise's internal blob storage

        ### Args:

        `blob_path`: file path to upload to

        `content`: the content of the file

        """
        logger.debug(f"Upload file to Superwise's internal blob storage {blob_path}")
        if not self._cloud_token or not self._is_cloud_token_active():
            self._refresh_cloud_token()
        try:
            file_url = self._put_in_storage(blob_path, content)
        except SuperWiseValidationError:
            raise
        except Exception as e:
            raise Exception(f'failed to upload blob to internal bucket - {e}')
        else:
            return file_url
