""" This module implement segment functionality  """
from superwise.controller.base import BaseController


class SegmentController(BaseController):
    """Class SegmentController - responsible for segment functionality"""

    def __init__(self, client, sw):
        """

        ### Args:

        `client`: superwise client object

        `sw`: superwise  object

        """
        super().__init__(client, sw)
        self.path = "admin/v1/segments"
        self.model_name = "Segment"
