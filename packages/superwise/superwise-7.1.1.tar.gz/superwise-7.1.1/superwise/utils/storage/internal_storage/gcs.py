from datetime import datetime

import requests
from google.auth import jwt
from google.cloud import storage
from google.oauth2.credentials import Credentials

from superwise import Config
from superwise.utils.client import Client
from superwise.utils.exceptions import SuperwiseStorageUploadGCSError
from superwise.utils.storage.gcs import GcsClient
from superwise.utils.storage.internal_storage.internal_storage import InternalStorage


class GCSInternalStorage(InternalStorage):
    def __init__(self, superwise_web_client: Client, bucket_name: str):
        super().__init__(superwise_web_client)
        self._bucket_name = bucket_name
        self._bucket = None
        self._gcs_client = GcsClient()

    def _put_in_storage(self, blob_name: str, content: str):
        return self._gcs_client.upload_string_to_bucket(content, blob_name, self._bucket)

    def _is_cloud_token_active(self) -> bool:
        expired_time = datetime.fromtimestamp(self._jwt_decoded['exp'])
        return datetime.utcnow() < expired_time

    def _refresh_cloud_token(self):
        super()._refresh_cloud_token()
        self._jwt_decoded = jwt.decode(self._cloud_token, verify=False)
        access_token = self._exchange_jwt_for_access_token()
        credentials = Credentials(token=access_token)
        gcs_client = storage.Client(credentials=credentials, project=Config.ENVIRONMENT)
        self._bucket = gcs_client.bucket(self._bucket_name)

    def _exchange_jwt_for_access_token(self):
        """
        This function takes a Signed JWT and exchanges it for a Google OAuth Access Token
        """
        params = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": self._cloud_token
        }
        resp = requests.post(self._jwt_decoded['aud'], data=params)

        if resp.ok:
            return resp.json()['access_token']

        raise SuperwiseStorageUploadGCSError(f'Failed to authenticate to google - {resp.text}')
