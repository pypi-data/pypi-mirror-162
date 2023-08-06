""" This module implement Segment model  """
from datetime import datetime
from typing import List
from typing import Optional
from typing import Union

from superwise.utils.exceptions import SuperwiseValidationException
from superwise.models.base import BaseModel
from superwise.resources.superwise_enums import SegmentCondition
from superwise.resources.superwise_enums import SegmentStatus


class SegmentConditionDefinition:
    def __init__(
        self,
        entity_name: str,
        condition: SegmentCondition,
        value: Union[List[str], List[float], List[bool], float, bool, str],
    ):
        self.entity_name = entity_name
        self.condition = condition
        self.value = value
        assert isinstance(condition, SegmentCondition)

    def to_dict(self):
        return dict(entity_name=self.entity_name, condition=self.condition.value, value=self.value)


class Segment(BaseModel):
    """ Segment model class """

    def __init__(
        self,
        id: int = None,
        model_id: int = None,
        name: str = None,
        status: SegmentStatus = None,
        definition: Optional[List[List[SegmentConditionDefinition]]] = None,
        definition_json: str = None,
        definition_query: str = None,
        created_at: datetime = None,
        created_by: str = None,
        archived_at: datetime = None,
        **kwargs,
    ):
        """
        ### Description:

        Constructor of Segment model class

        ### Args:

        `id`: id of segment

        `name`: name of segment (string)

        `status`: status of the model

        `definition`: definition of the query: list of list SegmentConditionDefinition or the condition in the
         inner list will have OR operator between them and all the inner list will have AND operator between them

        `definition_query`:

        `created_at`: the creation time of the segment

        `created_by`: the user created the segment

        `archived_at`: the archive time of the segment if exists

        """

        self.id = id
        self.model_id = model_id
        self.name = name
        self.status = status

        if definition is not None:
            self.definition_json = []
            for or_block_of_conditions in definition:
                if not isinstance(or_block_of_conditions, list):
                    raise SuperwiseValidationException(
                        "definition should be have be type of List[List[SegmentConditionDefinition]]"
                    )
                or_block_of_dict_conditions = []
                for condition in or_block_of_conditions:
                    if isinstance(condition, SegmentConditionDefinition):
                        or_block_of_dict_conditions.append(condition.to_dict())
                    else:
                        raise SuperwiseValidationException(f"{condition} is not instance of SegmentConditionDefinition")
                self.definition_json.append(or_block_of_dict_conditions)
        else:
            self.definition_json = definition_json
        self.definition_query = definition_query
        self.created_at = created_at
        self.created_by = created_by
        self.archived_at = archived_at
