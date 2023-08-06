import os
from enum import Enum


def get_bool(key, default):
    """
    ### Description:

    Cast string to bool

    ### Args:

    `key`: the key to get from ENV variable

    `default`: value to return if key not in ENV variable

    ### Return:
    True/False (bool)
    """

    v = os.environ.get(key, default)
    if v in ["False", "0", False]:
        return False
    else:
        return True


class DefaultValues(Enum):
    SUPERWISE_DOMAIN = 'superwise.ai'
    AUTH_URL = "https://auth.superwise.ai"
    ENVIRONMENT = "production"
    SUPERWISE_HOST = "portal.superwise.ai"
    MANAGED_AUTH_URL = "https://auth.managed.superwise.ai"


class Config:
    """
    ### Description:

    Configuration class - define some variables used by package
    """

    ENVIRONMENT = os.environ.get("ENVIRONMENT", DefaultValues.ENVIRONMENT.value)
    SUPERWISE_HOST = os.environ.get("SUPERWISE_HOST", DefaultValues.SUPERWISE_HOST.value)
    POOLING_INTERVAL_SEC = 15
    LIST_DROP_DATA_COLS = ["model_id", "version_id"]
    FILE_SIZE_LIMIT_BYTES = 100000000
    FILE_SIZE_PADDING = 50000000
    INTERNAL_BUCKET_SETTINGS = None
