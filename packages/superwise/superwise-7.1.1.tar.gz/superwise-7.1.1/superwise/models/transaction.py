""" This module implement Transaction model  """
from typing import List
from typing import Optional
from typing import Union

from superwise.models.base import BaseModel


class Transaction(BaseModel):
    """Transaction model"""

    def __init__(
        self,
        id: Optional[int] = None,
        model_id: Optional[int] = None,
        model_name: Optional[str] = None,
        version_id: Optional[Union[str, int]] = None,
        origin_url: Optional[str] = None,
        transaction_id: str = None,
        integration_type: Optional[str] = None,
        file_type: Optional[str] = None,
        status: Optional[str] = None,
        created_at: int = None,
        details: Optional[str] = None,
        num_of_records: Optional[str] = None,
        is_reviewed: bool = None,
        metadata: dict = None,
        **kwargs
    ):
        """
        ### Description:

        Constructor for Transaction class

        ### Args:

        `id`: id of model

        `model_id`: id of model

        `model_name`: name of the model

        `version_id`: id of the version

        `origin_url`: url of source file (Optional[str])

        `transaction_id`: transaction id (str)

        `integration_type`: Optional[str]

        `file_type`: Optional[str]

        `status`:  Optional[str]

        `created_at`: timestamp (int)

        `details`: Optional[str]

        `num_of_records`: Optional[str]

        `is_reviewed`: bool
        """
        self.id = id
        self.model_id = model_id
        self.model_name = model_name
        self.version_id = version_id
        self.origin_url = origin_url
        self.transaction_id = transaction_id
        self.integration_type = integration_type
        self.file_type = file_type
        self.status = status
        self.created_at = created_at
        self.details = details
        self.num_of_records = num_of_records
        self.is_reviewed = is_reviewed
        self.metadata = metadata
