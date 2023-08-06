""" This module implement notification functionality  """
from typing import Optional

from superwise.controller.base import BaseController
from superwise.models.notification import Notification
from superwise.resources.superwise_enums import NotificationType


class NotificationController(BaseController):
    """Class NotificationController - responsible for notification functionality"""

    def __init__(self, client, sw):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise  object

        """
        super().__init__(client, sw)
        self.path = "notification/v1/notifications"
        self.model_name = "Notification"

    def create_email_notification(self, name: str, email: str):
        """

          ### Args:

          `name`: notification name

          `email`: notification email

          """
        notification_model: Notification = Notification(
            name=name, notification_metadata={"target": [email]}, type=NotificationType.Email.value
        )
        return super().create(notification_model)

    def get(self, name: Optional[str] = None):
        """

          ### Args:

          `name`: notification name

          """
        if name is not None:
            return super().get({"name": name})
        return super().get({})
