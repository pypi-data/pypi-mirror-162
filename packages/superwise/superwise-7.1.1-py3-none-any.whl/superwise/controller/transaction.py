""" This module implement data functionality  """
import json
import re
import warnings
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd

from superwise.controller.base import BaseController
from superwise.utils.exceptions import SuperwiseValidationException
from superwise.utils.file_path import extract_file_extension
from superwise.utils.storage.azure import AzureClientReader
from superwise.utils.storage.gcs import GcsClient
from superwise.utils.storage.local import load_from_local_storage
from superwise.utils.storage.s3 import S3Client


class TransactionController(BaseController):
    """Transaction Controller is in-charge for create transaction using file or batch request """

    def __init__(self, client, sw, internal_bucket):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise  object

        """
        super().__init__(client, sw)
        self.path = "gateway/v1/transaction"
        self.model_name = None
        self._internal_bucket = internal_bucket

    def _upload_string_to_internal_bucket(self, data, file_prefix, file_extension):
        file_name = self._internal_bucket.generate_file_name(prefix=file_prefix,
                                                             extension=file_extension)
        blob_path = f"landing/{file_name}"
        return self._internal_bucket.upload(blob_path=blob_path,
                                            content=data)

    def log_records(
        self,
        model_id: str,
        records: List[dict],
        version_id: Optional[Union[str, int]] = None,
        metadata: Optional[Dict] = None,
    ):
        """
        ### Description:

        Send list of records

        ### Args:

        `model_id`:  string - model id

        `version_id`:  int - version id of the model - Optional[for prediction records]

        `records`:  List[dict] - list of records of data,  each record is a dict.

        `transaction_id`:  string - uuid of the log operation

        `metadata`:  dict - dict of metadata of transaction

        """
        warnings.warn("Passing version name will be deprecated soon, pass version ID instead")
        self.logger.info(f"Send records with params : model_id={model_id}, version_id={version_id}")
        records_df = pd.DataFrame(records)

        records = json.loads(records_df.to_json(orient="records", date_format="iso"))
        payload = dict(records=records, model_id=model_id)
        if version_id is not None:
            payload["version_id"] = version_id
        self._validate_metadata(metadata)
        payload["metadata"] = metadata
        r = self.client.post(self.client.build_url("{}".format(self.path + "/records")), payload)
        self.logger.info("file_log server response: {}".format(r.content))
        return r.json()

    def log_from_s3(
        self,
        file_path: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        role_arn: Optional[str] = None,
        version_id: Optional[int] = None,
        model_id: Optional[int] = None,
        metadata: Optional[dict] = None,
    ):

        """
        ### Description:

        Upload file from s3 bucket to superwise bucket.</br>
        The permission for the client s3 bucket should be by providing aws_access_key_id and aws_secret_access_key or

        ### Args:

        `file_path`:  s3 url path

        `aws_access_key_id`:

        `aws_secret_access_key`: .

        `role_arn`:  AWS Role arn

        `version_id`: string - id of version (optional)

        `model_id`: string - id of model (optional)

        """
        s3_obj = S3Client()
        key, content = s3_obj.get_s3_file(file_path, aws_access_key_id, aws_secret_access_key, role_arn)
        file_extension = extract_file_extension(file_path)
        superwise_file_path = self._upload_string_to_internal_bucket(data=content.read(),
                                                                     file_prefix='s3',
                                                                     file_extension=file_extension)
        return self.log_file(
            file_path=superwise_file_path,
            _origin_path=file_path,
            version_id=version_id,
            model_id=model_id,
            metadata=metadata,
        )

    def log_from_gcs(
        self,
        file_path: str,
        service_account: Dict,
        version_id: Optional[str] = None,
        model_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """
        ### Description:

        Upload file from gcs bucket to superwise bucket

        ### Args:

        `file_path`:  gcs file path

        `service_account`: dict of the service account.

        `transaction_id`: string - uuid of the log operation

        `version_id`: string - id of version (optional)

        `model_id`: string - id of model (optional)

        `metadata`:  dict - dict of metadata of transaction

        """
        _gcs = GcsClient()

        key, data = _gcs.get_file_from_gcs(file_path, service_account)
        file_extension = extract_file_extension(file_path)
        superwise_file_path = self._upload_string_to_internal_bucket(data=data,
                                                                     file_prefix='gcs',
                                                                     file_extension=file_extension)
        return self.log_file(
            file_path=superwise_file_path,
            _origin_path=file_path,
            version_id=version_id,
            model_id=model_id,
            metadata=metadata,
        )

    def log_from_local_file(
        self,
        file_path: str,
        version_id: Optional[str] = None,
        model_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):
        """
        ### Description:

        Upload file from local machine to superwise bucket

        ### Args:

        `file_path`: Local path to file

        `version_id`: string - id of version (optional)

        `model_id`: string - id of model (optional)

        `metadata`:  dict - dict of metadata of transaction
        """
        filename, data = load_from_local_storage(file_path)
        file_extension = extract_file_extension(filename)
        superwise_file_path = self._upload_string_to_internal_bucket(data=data,
                                                                     file_prefix='fs',
                                                                     file_extension=file_extension)
        return self.log_file(
            file_path=superwise_file_path,
            _origin_path=f"file://{filename}",
            version_id=version_id,
            model_id=model_id,
            metadata=metadata,
        )

    def log_from_azure(
            self,
            azure_uri: str,
            connection_string: str,
            version_id: Optional[str] = None,
            model_id: Optional[str] = None,
            metadata: Optional[dict] = None,
    ):
        """
        ### Description:

        Upload file from Azure Blob Storage to superwise bucket

        ### Args:

        `azure_uri`: URI of file (URI scheme is the Azure Blob Filesystem driver: abfs://my_container/path/to/blob)

        `connection_string`: Azure Storage connection string

        `version_id`: string - id of version (optional)

        `model_id`: string - id of model (optional)

        `metadata`:  dict - dict of metadata of transaction
        """
        azure_reader_client = AzureClientReader(connection_string)
        content = azure_reader_client.get_file_from_blob_storage(azure_uri, validate_size=True)
        file_extension = extract_file_extension(azure_uri)
        superwise_file_path = self._upload_string_to_internal_bucket(content,
                                                                     file_prefix='azure',
                                                                     file_extension=file_extension)
        return self.log_file(
            file_path=superwise_file_path,
            _origin_path=azure_uri,
            version_id=version_id,
            model_id=model_id,
            metadata=metadata,
        )

    def _validate_metadata(self, metadata: Optional[Dict] = None):
        if metadata:
            for k, v in metadata.items():
                if type(v) not in [str, int, float, bool]:
                    raise SuperwiseValidationException(
                        f"metadata value {v} of  key {k} is not one of: integer, string or float"
                    )

    def log_file(
        self,
        file_path: str,
        _origin_path: Optional[str] = None,
        version_id: Optional[str] = None,
        model_id: Optional[str] = None,
        metadata: Optional[dict] = None,
    ):

        """
        ### Description:

        Stream data of a given file path

        ### Args:

        `file_path`:  url for file stored in cloud str

        `transaction_id`: string - uuid of the log operation

        `version_id`: string - id of version (optional)

        `model_id`: string - id of model (optional)

        `metadata`:  dict - dict of metadata of transaction

        ### Return:

        json object  represent the transaction from server
        """
        warnings.warn("Passing version name inside the file will be deprecated soon, pass version ID instead")
        self.logger.info(f"Log file {file_path}")
        pattern = "((s3|gs|abfs):\/\/.+)"
        if not re.match(pattern, file_path):
            raise SuperwiseValidationException(
                "transaction file failed because of wrong file path. file path should be gcs, s3 or azure (abfs)."
            )
        self._validate_metadata(metadata)

        params = {"file": file_path, "version_id": version_id, "model_id": model_id, "metadata": metadata}
        if _origin_path is not None:
            params["origin_path"] = _origin_path

        r = self.client.post(url=self.client.build_url("{}".format(self.path + "/file")), params=params)
        self.logger.info("transaction file server response: {}".format(r.content))
        return r.json()

    def get(self, transaction_id: str):
        """
         ### Description:

         Get transaction by transaction id

         ### Args:

         `transaction_id`:  string - transaction_id to fetch from server

         ### Return:

         Transaction object
         """

        self.logger.info(f"Get transaction by transaction id {transaction_id}")
        response = self.client.get(
            url=self.client.build_url("{}".format("integration/v1/transactions" + f"/{transaction_id}"))
        )
        self.logger.info("transaction file server response: {}".format(response.content))
        transaction = self.parse_response(response, "Transaction", is_return_model=True)
        return transaction
