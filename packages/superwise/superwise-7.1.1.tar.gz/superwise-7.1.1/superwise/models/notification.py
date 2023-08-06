""" This module implement Notification model  """
import datetime
import warnings

from superwise.models.base import BaseModel


class Notification(BaseModel):
    """ Notification model class """

    def __init__(
        self,
        id: int = None,
        name: str = None,
        type: str = None,
        notification_metadata=None,
        created_at: datetime = None,
        last_delivery_status=None,
        last_delivery_ts: datetime = None,
        is_enabled: bool = True,
        is_hide: bool = False,
        **kwargs
    ):
        """
        ### Description:

        Constructor for Notification class

        ### Args:

        `id`: id of model

        `type`: type of the notification

        `name`: name of notification

        `last_delivery_ts`: description for the model

        `notification_metadata`:

        `created_at`:
        """
        self.id = id
        self.name = name
        self.last_delivery_ts = last_delivery_ts
        self.is_hide = is_hide
        self.is_enabled = is_enabled
        self.type = type
        self.notification_metadata = notification_metadata
        self.created_at = created_at
        self.last_delivery_status = last_delivery_status
