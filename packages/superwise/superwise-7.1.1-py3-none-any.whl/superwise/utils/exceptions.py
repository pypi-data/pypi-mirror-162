""" This module implement suprewise custom exceptions  """


class SuperWiseInternalServerError(Exception):
    """  SuperWiseInternalServerError customn exception """


class SuperWiseValidationError(Exception):
    """  SuperWiseValidationError customn exception """


class SuperwiseException(SuperWiseValidationError):
    """  SuperwiseException customn exception """


class SuperwiseTokenException(SuperWiseValidationError):
    """  SuperwiseException customn exception """


class SuperwiseValidationException(SuperWiseValidationError):
    """  SuperwiseValidationException customn exception """


class SuperwiseUnsupportedException(SuperWiseValidationError):
    """  SuperwiseValidationException customn exception """


class SuperwiseAuthException(SuperWiseValidationError):
    """  SuperwiseAuthException customn exception """


class SuperwiseServiceAccountException(SuperWiseValidationError):
    """  SuperwiseAuthException custom exception """


class SuperwiseStorageDownloadS3Error(SuperWiseValidationError):
    """  SuperwiseStorageDownloadS3Error custom exception """


class SuperwiseStorageDownloadGCSError(SuperWiseValidationError):
    """  SuperwiseStorageDownloadGCSError custom exception """


class SuperwiseStorageUploadGCSError(SuperWiseValidationError):
    """  SuperwiseStorageUploadGCSError custom exception """


class SuperwiseStorageUploadAzureError(SuperWiseValidationError):
    """  SuperwiseStorageUploadAzureError custom exception """


class SuperwiseRefreshCloudTokenError(Exception):
    """ SuperwiseRefreshCloudTokenError custom exception """


class SuperwiseTimeoutError(Exception):
    """ Superwise timeout exception"""


class SuperwiseDatasetFailureError(Exception):
    """ Superwise dataset creation error """


class SuperwiseFileTooLargeError(Exception):
    """ Superwise file too large error """
