from http import HTTPStatus

import jwt
import pytest
import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from google.cloud import storage
from google.oauth2 import service_account
from requests import Response

from superwise import Client
from superwise import Superwise
from superwise.utils.storage.internal_storage.azure import AzureInternalStorage
from superwise.utils.storage.internal_storage.gcs import GCSInternalStorage
from superwise.utils.storage.internal_storage.internal_storage import CloudProvider, InternalStorage


@pytest.fixture(scope="function")
def mock_gcp_internal_bucket(monkeypatch):
    monkeypatch.setattr(
        GCSInternalStorage,
        "_exchange_jwt_for_access_token",
        lambda *args, **kwargs:
        "access token",
    )

    monkeypatch.setattr(GCSInternalStorage, '_is_cloud_token_active', lambda *args, **kwargs: True)
    monkeypatch.setattr(GCSInternalStorage, '_put_in_storage', lambda *args, **kwargs: 'gs://somepath')


@pytest.fixture(scope="function")
def mock_refresh_internal_bucket_token(monkeypatch):
    def mock_refresh(self, *args, **kwargs):
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        self._cloud_token = jwt.encode({'payload': 'aaaaa'}, private_key, algorithm="RS256")

    monkeypatch.setattr(InternalStorage, '_refresh_cloud_token', mock_refresh)


@pytest.fixture(scope="function")
def mock_azure_internal_bucket(monkeypatch):
    put_response = Response()
    put_response.status_code = HTTPStatus.OK
    monkeypatch.setattr(AzureInternalStorage, '_is_cloud_token_active', lambda *args, **kwargs: True)
    put_response = Response()
    put_response.status_code = 200
    monkeypatch.setattr(requests, 'put', lambda *args, **kwargs: put_response)


@pytest.fixture(scope="function")
def mock_get_token(monkeypatch):
    monkeypatch.setattr(
        Client,
        "get_token",
        lambda *args, **kwargs:
        "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IjQ3ZDdmMDg2In0.eyJzdWIiOiI5YzNlZmUxZC03NGNlLTRlZTItYTMyOC1kMWZmNmQyMDAyM2YiLCJlbWFpbCI6InN3X2JhcmFrQHN1cGVyd2lzZS5haSIsInVzZXJNZXRhZGF0YSI6e30sInRlbmFudElkIjoiYmFyYWsiLCJyb2xlcyI6WyJWaWV3ZXIiXSwicGVybWlzc2lvbnMiOlsiZmUuc2VjdXJlLndyaXRlLnVzZXJBcGlUb2tlbnMiLCJmZS5zZWN1cmUuZGVsZXRlLnVzZXJBcGlUb2tlbnMiLCJmZS5zZWN1cmUucmVhZC51c2VyQXBpVG9rZW5zIl0sIm1ldGFkYXRhIjp7fSwiY3JlYXRlZEJ5VXNlcklkIjoiNDg5ZmM5Y2YtZDlhYy00MWMwLWJmM2ItN2VhNDUyNDY4ODEyIiwidHlwZSI6InVzZXJBcGlUb2tlbiIsInVzZXJJZCI6IjQ4OWZjOWNmLWQ5YWMtNDFjMC1iZjNiLTdlYTQ1MjQ2ODgxMiIsImlhdCI6MTYzNjY0ODIyMywiZXhwIjoxNjM2NzM0NjIzLCJpc3MiOiJmcm9udGVnZyJ9.qhEclIsSpfwXpCTFb8qhKpizRWtpQSnkE7VMsy9Et3guLcOcTiTVZ2wOJPmemtL3g3AStKH2jFSOEwQOoqnvgSR3dum9I_Ae3UwrFNRnM3EqOz7UsD0cJAd1AYy-69-67o5oX9A2U4MPZSA5Dr5Edbvn86-AsBJhADGDs5AyEyuGmlJTq0ACGAmoC8qZlxwnOsn9wIzTiQVU7085M73n5iJ26SNhsy4KNpU-8oR2lC1akDroHzL8aIr5dAWSWZz_cfcyWQyC1gqb4_ZAvG1GXiKwsGW2irFyfGoD9zrwMoMGuWXKCbXnHxIzuv8ImX_cRVPXq5xVBYUXwODr83Q3FA",
    )


@pytest.fixture(scope="function")
def mock_gcp_client(monkeypatch):
    class GCSClient:
        def __init__(self, *args, **kwargs):
            self.name = "test"
            self.size = 1000

        def bucket(self, bucket_name):
            return GCSClient()

        def get_blob(self, file_name):
            return GCSClient()

        def blob(self, file_name):
            return GCSClient()

        def download_as_string(self):
            return "asdasdaas"

        def upload_from_string(self, data):
            return None

    monkeypatch.setattr(service_account.Credentials, "from_service_account_info", lambda *args, **kwargs: "")
    monkeypatch.setattr(storage, "Client", lambda *args, **kwargs: GCSClient())


# running in all cloud providers environments
@pytest.fixture(scope="function", params=[provider.value for provider in CloudProvider])
def mock_admin_settings(monkeypatch, request):
    settings = {
        'file_upload_settings': {
            'cloud_provider': request.param,
            'azure_account_name': 'test',
            'azure_container_name': 'test',
            'gcs_bucket_name': 'test'
        }
    }
    monkeypatch.setattr(Superwise, '_get_admin_settings', lambda *args, **kwargs: settings)


@pytest.fixture(scope="function")
def sw(mock_admin_settings,
       mock_get_token,
       mock_refresh_internal_bucket_token,
       mock_gcp_internal_bucket,
       mock_azure_internal_bucket):
    return Superwise(client_id="test", secret="test")
