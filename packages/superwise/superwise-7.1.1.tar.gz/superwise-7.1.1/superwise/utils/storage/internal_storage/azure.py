from datetime import datetime
from urllib.parse import parse_qs

from superwise.utils.client import Client
from superwise.utils.exceptions import SuperwiseStorageUploadAzureError, SuperwiseRefreshCloudTokenError
from superwise.utils.storage.azure import AzureClientUploader
from superwise.utils.storage.internal_storage.internal_storage import InternalStorage


class AzureInternalStorage(InternalStorage):
    url = "https://{account_name}.blob.core.windows.net/{container_name}/{blob_name}"

    def __init__(
            self,
            superwise_client: Client,
            account_name: str,
            container_name: str):
        super().__init__(superwise_client)
        self._account_name = account_name
        self._azure_client = AzureClientUploader(account_name, container_name)

    def _is_cloud_token_active(self) -> bool:
        parsed_token = parse_qs(self._cloud_token)
        se = parsed_token['se'][0]
        expired_time = datetime.strptime(se, "%Y-%m-%dT%H:%M:%SZ")
        return datetime.utcnow() < expired_time

    def _put_in_storage(self, blob_name: str, content: str):
        try:
            url = self._azure_client.upload(content, blob_name, self._cloud_token)
        except SuperwiseRefreshCloudTokenError:
            # token has expired between the time of checking token expiration and sending the actual request
            self._refresh_cloud_token()
            url = self._azure_client.upload(content, blob_name, self._cloud_token)
        except Exception as e:
            raise SuperwiseStorageUploadAzureError(f'Failed upload file to superwise storage {blob_name} with ext {e}')

        return url
