""" This module implement tasks functionality  """
import json
from typing import Dict
from typing import List

import pandas as pd
from pandas import DataFrame
from requests import Response

from superwise.controller.base import BaseController
from superwise.models.notification import Notification
from superwise.resources.superwise_enums import NotifyUpon
from superwise.resources.superwise_enums import ScheduleCron


class PolicyController(BaseController):
    """Class ModelController - responsible for task functionality"""

    def __init__(self, client, sw):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise  object

        """
        super().__init__(client, sw)
        self.path = "monitor/v1/policy"
        self.model_name = "Policy"

    def get_policy_templates(self) -> DataFrame:
        """
        ### Description:
        Get all the available templates
        """

        response = self.client.get(self.client.build_url(f"{self.path}/templates"))

        assert response.text != "" and response.text != "", "Something went wrong: 0 templates received"

        fields_to_display = ["name", "description"]
        templates: List[Dict] = response.json()

        return pd.DataFrame(templates)[fields_to_display]

    def create_policy_from_template(
        self,
        model_id: int,
        template_name: str,
        notify_upon: NotifyUpon,
        notification_channels: List[Notification],
        schedule: ScheduleCron,
        policy_name: str = None,
        minimal_quantity: int = 0,
        monitor_offset: int = 1,
    ) -> Response:
        """
        ### Description:
        Used for creation of policy from one of the available templates

        ### Args:

        `model_id`: id of the model which the policy will monitor

        `template_name`: The name of the template which the policy will be created from

        `notify_upon`: When you should be notified

        `notification_channels`: List of all the notifications channels you would like to receive notification when the
         policy will find violations

        `schedule`: Cronstring - defines when the policy will be run and data will be sampled for violations.

        `policy_name`: Optional - The name of the policy that will be created, if not supplied the name will be the
        taken from the template name and the model's id

        `minimal_quantity`: Optional - Minimum threshold value for ignoring sampling/aggregation of time frames with
         less than
        the threshold of rows.

        `monitor_offset`: Optional - Amount of days for delay until they are monitored, useful when you need to add
         label data or
        wait until all the data is available.

          """
        notification_channels_ids = list(map(lambda notification: notification.id, notification_channels))
        payload = {
            "template_name": template_name,
            "notify_upon": notify_upon.value,
            "notification_channels": notification_channels_ids,
            "model_id": model_id,
            "schedule": schedule.value,
            "policy_name": policy_name,
            "minimal_quantity": minimal_quantity,
            "monitor_offset": monitor_offset,
        }

        return self.client.post(self.client.build_url(f"{self.path}/templates"), payload)
