from datetime import datetime
from http import HTTPStatus
from urllib.parse import urlparse

import requests
from azure.storage.blob import BlobClient

from superwise.utils.exceptions import SuperwiseStorageUploadAzureError, SuperwiseRefreshCloudTokenError
from superwise.utils.storage import validate_file_size


class AzureClientUploader:
    url = "https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"
    internal_services_valid_url = "abfs://{container_name}/{blob_name}"

    def __init__(self, account_name, container_name):
        self._account_name = account_name
        self._container_name = container_name

    def upload(self, content, blob_name, sas_token):
        url = self.url.format(
            account_name=self._account_name,
            container_name=self._container_name,
            blob_name=blob_name,
        )

        headers = {
            "x-ms-date": datetime.utcnow().strftime('%a %B %d %T %Y'),
            "x-ms-blob-type": "BlockBlob"
        }
        response = requests.put(url, data=content, headers=headers, params=sas_token)
        if response.status_code == HTTPStatus.FORBIDDEN:
            raise SuperwiseRefreshCloudTokenError(f"Forbidden access to azure's container {self._container_name}, "
                                                  f"try to refresh the sas token")
        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            raise SuperwiseStorageUploadAzureError(f'Failed upload file to superwise storage {blob_name} with ext {e}')
        else:
            return self.internal_services_valid_url.format(container_name=self._container_name, blob_name=blob_name)


class AzureClientReader:
    def __init__(self, connection_string):
        self.connection_string = connection_string

    def get_file_from_blob_storage(self, file_path, validate_size=False):
        container = self._extract_container_name_from_path(file_path)
        blob_name = self._extract_blob_name_from_path(file_path)
        blob_client = BlobClient.from_connection_string(
            conn_str=self.connection_string, container_name=container, blob_name=blob_name
        )
        if validate_size:
            size = blob_client.get_blob_properties()["size"]
            validate_file_size(file_path, size)

        data = blob_client.download_blob().readall()
        return data

    @staticmethod
    def _extract_container_name_from_path(file_path):
        """
        'abfs://my_container/my/blob' --> 'my_container'
        """
        parsed_path = urlparse(file_path)
        container = parsed_path.hostname

        return container

    @staticmethod
    def _extract_blob_name_from_path(file_path):
        """
        'abfs://my_container/my/blob' --> 'my/blob'
        """
        parsed_path = urlparse(file_path)
        # removing first slash(/)
        blob_name = parsed_path.path[1:]

        return blob_name
