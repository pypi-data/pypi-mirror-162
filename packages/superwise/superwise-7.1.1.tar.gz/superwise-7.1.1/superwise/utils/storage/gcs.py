""" This module implement gcs client functionality  """
import google.api_core.exceptions
from google.cloud import storage
from google.oauth2 import service_account as gcp_service_account

from superwise import logger
from superwise.utils.exceptions import SuperwiseFileTooLargeError
from superwise.utils.exceptions import SuperwiseStorageDownloadGCSError
from superwise.utils.exceptions import SuperwiseStorageUploadGCSError
from superwise.utils.singelton import singleton
from superwise.utils.storage import extract_directory
from superwise.utils.storage import validate_file_size


@singleton
class GcsClient:
    def __init__(self):
        self.logger = logger

    def get_file_from_gcs(self, file_path, service_account: dict = None, validate_size: bool = False):
        """
        ### Description:

        get the content of file from gcs

        ### Args:

        `file_path`:  the file patch

        `service_account`:  ssuperwise service account object

        ### Return:

        a string of the object (file) content
        """
        if not str(file_path).startswith("gs://"):
            self.logger.error("Failed upload file to superwise storage")
            raise Exception("file_path must start with 'gs://'")
        self.logger.info("Download file {} from gcs".format(file_path))
        bucket, key = extract_directory(file_path)
        try:
            customer_bucket = self.create_gcs_bucket_connection(bucket, service_account)
            blob = customer_bucket.get_blob(key)
            if validate_size:
                self._validate_blob_size(blob)
            data = blob.download_as_string()
        except SuperwiseFileTooLargeError:
            raise
        except Exception as e:
            self.logger.error(f"Error download file {file_path} from gcs with ext{e}")
            raise SuperwiseStorageDownloadGCSError(f"Error download file {file_path} from gcs")
        return key, data

    def create_gcs_bucket_connection(self, bucket_name: str, service_account: dict = None):
        """
        ### Description:

        get connection to gcs bucket

        ### Args:

        `bucket_name`: gcs bucket name

        `service_account`: superwise service account object

        """
        try:
            self.logger.debug(f"Create connection to superwise bucket {bucket_name}")
            credentials = None
            if service_account:
                credentials = gcp_service_account.Credentials.from_service_account_info(service_account)
            gcs_client = storage.Client(credentials=credentials)
            bucket_connection = gcs_client.bucket(bucket_name)
            return bucket_connection
        except Exception as e:
            self.logger.error(f"Error create connection to superwise bucket {bucket_name}")
            raise Exception(f"Error create connection to superwise bucket {bucket_name}")

    def upload_string_to_bucket(self, data, blob_name, bucket):
        try:
            self.logger.debug(f"Upload file to superwise bucket {blob_name}")
            blob = bucket.blob(blob_name)
            blob.upload_from_string(data=data)
            return f"gs://{bucket.name}/{blob_name}"
        except google.api_core.exceptions.Forbidden as e:
            raise SuperwiseStorageUploadGCSError(f"Failed upload file to superwise storage {blob_name} with ext {e}")
        except Exception as e:
            self.logger.error(f"Failed upload file to superwise storage {blob_name} with ext {e}")
            raise SuperwiseStorageUploadGCSError(f"Failed upload file to superwise storage {blob_name} with ext {e}")

    @staticmethod
    def _validate_blob_size(blob):
        logger.debug(f"Blob {blob.name} size is {blob.size}")
        size = blob.size

        validate_file_size(file_path=blob.name, file_size=size)
