""" This module implement s3 client functionality  """
from typing import Optional

import boto3

from superwise import logger
from superwise.utils.exceptions import SuperwiseException
from superwise.utils.exceptions import SuperwiseFileTooLargeError
from superwise.utils.exceptions import SuperwiseStorageDownloadS3Error
from superwise.utils.singelton import singleton
from superwise.utils.storage import extract_directory
from superwise.utils.storage import validate_file_size


@singleton
class S3Client:
    def __init__(self):
        self.logger = logger

    def get_s3_file(
        self,
        file_path: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        role_arn: Optional[str] = None,
        validate_size: bool = False,
    ):
        """
        ### Description:
        get a given s3 file from s3

        ### Args:
        `file_path`:  file path string

        `aws_access_key_id`:  aws access key id string

        `aws_secret_access_key`:  aws secret key  string

        `role_arn`:  aws role arn string

        ### Return:
        a tuple the s3 file key (path) and the content of the file
        """
        if not str(file_path).startswith("s3://"):
            self.logger.error(f"Failed upload file to superwise storage {file_path}")
            raise Exception("file_path must start with 's3://'")
        try:
            self.logger.info("Download file {} from s3".format(file_path))
            bucket, key = extract_directory(file_path)
            s3_client = self._create_s3_client(
                aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, role_arn=role_arn
            )
            if validate_size:
                self._validate_object_size(file_path, s3_client)
            resp = s3_client.get_object(Bucket=bucket, Key=key)
            return key, resp["Body"]
        except SuperwiseFileTooLargeError:
            raise
        except Exception as e:
            self.logger.error(f"Error download file from customer s3 bucket {file_path} with ext {e}")
            raise SuperwiseStorageDownloadS3Error(f"Error download file from customer s3 bucket {file_path}")

    def _create_s3_client(self, aws_access_key_id: str = None, aws_secret_access_key: str = None, role_arn: str = None):
        """
        ### Description:
        create s3   client to work with

        ### Args:
        `aws_access_key_id`:  aws access key id string

        `aws_secret_access_key`:  aws secret key  string

        `role_arn`:  aws role arn string

        ### Return:
        boto3.client("s3") object
        """
        try:
            if role_arn is not None:
                self.logger.debug("Create S3 client from role_arn")
                sts_client = boto3.client("sts")
                assumed_role_object = sts_client.assume_role(RoleArn=role_arn, RoleSessionName="superwise-session")
                credentials = assumed_role_object["Credentials"]

                return boto3.client(
                    "s3",
                    aws_access_key_id=credentials["AccessKeyId"],
                    aws_secret_access_key=credentials["SecretAccessKey"],
                    aws_session_token=credentials["SessionToken"],
                )
            elif aws_access_key_id is not None and aws_secret_access_key is not None:
                self.logger.debug("Create S3 client with aws access key and secret key")
                return boto3.client(
                    "s3", aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key
                )

            else:
                self.logger.debug("Create s3 client with out any params")
                return boto3.client("s3")
        except Exception as e:
            self.logger.error(f"Error create s3 client, ext {e}")
            raise SuperwiseException("Error create s3 client - role arn or access and secret keys not provided")

    @staticmethod
    def _validate_object_size(file_url: str, client):
        logger.debug(f"Get metadata from S3 for file_url: {file_url}")
        bucket_name, object_key = extract_directory(file_url)
        metadata = client.head_object(Bucket=bucket_name, Key=object_key)
        size = metadata["ContentLength"]

        validate_file_size(file_path=file_url, file_size=size)
