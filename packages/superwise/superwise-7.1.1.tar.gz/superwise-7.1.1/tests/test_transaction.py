import json
import os.path

import boto3
import pytest
import requests
from requests import Response

from project_root import PROJECT_ROOT
from superwise.utils.storage.azure import AzureClientReader
from superwise.utils.exceptions import SuperwiseValidationException
from superwise.models.transaction import Transaction


@pytest.fixture(scope="function")
def mock_transaction_requests(monkeypatch):
    the_response = Response()
    the_response._content = b'{ "transaction_id" : "123" ,"metadata" : {}}'
    the_response.status_code = 201
    get_response = Response()
    get_response._content = b"{\"created_at\": 1639668801319, \"details\": \"predictions columns diff: {'email_11174', 'linking_identity_230', 'linking_strong_187', 'linking_identity_637', 'ip_country_code', 'linking_identity_765', 'linking_identity_636', 'is_digital', 'linking_online_755', 'linking_strong_169', 'ip_organization', 'linking_online_519', 'order_total_spent', 'shipping_province_code', 'bin_country_code', 'prediction_probability', 'periodic_310', 'order_83', 'customer_49', 'vendor_id', 'periodic_360', 'currency_code', 'linking_online_744', 'product_v3', 'merchant_id', 'decision_reason', 'technical_plan', 'cc_69', 'ts', 'periodic_135', 'linking_strong_780', 'beacon_309', 'linking_identity_778', 'periodic_8', 'linking_online_520', 'approve_threshold', 'cc_822', 'action_review', 'order_source', 'billing_province_code', 'order_submission_reason', 'cc_823', 'order_language', 'linking_identity_849', 'customer_410', 'cc_223', 'email_186', 'shipping_country_code', 'linking_strong_38', 'order_type', 'linking_identity_31', 'customer_v2', 'order_245', 'ip_region', 'linking_strong_193', 'billing_country_code', 'name_11172', 'email_953', 'linking_identity_395', 'periodic_311', 'ip_city', 'cc_v8', 'riskimal_class', 'ip_v3', 'cc_v6', 'linking_online_779', 'linking_online_745', 'prediction_value', 'email_73', 'linking_identity_72'}label columns diff {'label'}\", \"file_type\": null, \"id\": 661218, \"integration_type\": \"RECORD\", \"is_reviewed\": false, \"num_of_records\": \"80\", \"origin_url\": \"gs://superwise-oryandna-development/origin/year=2021/month=12/day=16/8000db7c-5e85-11ec-90b8-42013606f5d0.parquet\", \"status\": \"Failed\", \"model_id\": null, \"model_name\": null, \"transaction_id\": \"8000db7c-5e85-11ec-90b8-42013606f5d0\", \"version_id\": null}"
    get_response.status_code = 200
    monkeypatch.setattr(requests, "post", lambda *args, **kwargs: the_response)
    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: get_response)


@pytest.fixture(scope="function")
def mock_azure_blob_reader(monkeypatch):
    monkeypatch.setattr(AzureClientReader, 'get_file_from_blob_storage', lambda *args, **kwargs: 'content')


@pytest.fixture(scope="function")
def mock_boto_client(monkeypatch):
    class BotoClient:
        def __init__(self, *args, **kwargs):
            pass

        def get_object(self, *args, **kwargs):
            class ObjectResposne:
                def read(self):
                    return "blablabla"

            return dict(Body=ObjectResposne())

    monkeypatch.setattr(boto3, "client", lambda *args, **kwargs: BotoClient())


@pytest.fixture(scope="function")
def get_transaction_records_payload():
    with open(f"{PROJECT_ROOT}/tests/resources/transaction/records_payload.json") as f:
        return json.loads(f.read())


def test_transaction_records(mock_transaction_requests, sw, get_transaction_records_payload):
    status = sw.transaction.log_records(model_id=1, records=get_transaction_records_payload)
    assert isinstance(status, dict) and "transaction_id" in status.keys()
    status = sw.transaction.log_records(model_id="test", version_id=1, records=get_transaction_records_payload)
    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_file(mock_transaction_requests, sw):
    status = sw.transaction.log_file("gs://fvsdfvfdv")
    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_with_wrong_file_path(mock_transaction_requests, sw):
    with pytest.raises(SuperwiseValidationException):
        sw.transaction.log_file("wrong path")


def test_transaction_upload_from_gcs(mock_transaction_requests, mock_gcp_client, sw):
    status = sw.transaction.log_from_gcs(
        file_path="gs://superwise-oryan-test/new_integration_tests_binary_classification_predictions.csv",
        service_account={},
        metadata={"test": "value"},
    )

    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_upload_from_s3(mock_transaction_requests, mock_boto_client, sw):
    status = sw.transaction.log_from_s3(
        file_path="s3://superwise-oryan-test/new_integration_tests_binary_classification_predictions.csv",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        metadata={"test": "value"},
    )
    assert isinstance(status, dict) and "transaction_id" in status.keys()


def test_transaction_upload_from_local_file(mock_transaction_requests, sw):
    status = sw.transaction.log_from_local_file(
        file_path=os.path.join(PROJECT_ROOT, "tests", "resources", "transaction", "local_records_file.json"),
        metadata={"test": "value"},
    )
    assert isinstance(status, dict) and "transaction_id" in status.keys()
    assert isinstance(status, dict) and "metadata" in status.keys()


def test_transaction_upload_from_azure(mock_transaction_requests, mock_azure_blob_reader, sw):
    status = sw.transaction.log_from_azure(azure_uri='abfs://container/blob',
                                           connection_string='connection string',
                                           metadata={"test": "value"})

    assert isinstance(status, dict) and "transaction_id" in status.keys()
    assert isinstance(status, dict) and "metadata" in status.keys()


def test_transaction_upload_from_not_existing_local_file(sw):
    with pytest.raises(FileNotFoundError):
        sw.transaction.log_from_local_file("invalid_path")


def test_get_transaction(mock_transaction_requests, sw):
    transaction = sw.transaction.get(transaction_id="blabla")
    assert isinstance(transaction, Transaction)
