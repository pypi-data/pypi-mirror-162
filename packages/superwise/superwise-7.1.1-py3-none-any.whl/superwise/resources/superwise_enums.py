from enum import Enum


class DataEntityRole(Enum):
    """ Data Entity Role enum"""

    ID = "id"
    TIMESTAMP = "time stamp"
    FEATURE = "feature"
    PREDICTION_PROBABILITY = "prediction probability"
    PREDICTION_VALUE = "prediction value"
    LABEL = "label"
    LABEL_TIMESTAMP = "label time stamp"
    LABEL_WEIGHT = "label weight"
    METADATA = "metadata"


class ModelTypes(Enum):
    """ Data Types enum"""

    BINARY_CLASSIFICATION = "Binary Classification"
    BINARY_ESTIMATION = "Binary Estimation"
    REGRESSION = "Regression"
    MULTICLASS_CLASSIFICATION = "Multiclass Classification"


class FeatureType(Enum):
    """ Feature Type enum"""

    NUMERIC = "Numeric"
    BOOLEAN = "Boolean"
    CATEGORICAL = "Categorical"
    TIMESTAMP = "Timestamp"
    UNKNOWN = "Unknown"


class CategoricalSecondaryType(Enum):
    """ Categorical Secondary Type enum"""

    CONSTANT = "Cat_constant"
    DENSE = "Cat_dense"
    SPARSE = "Cat_sparse"


class NumericSecondaryType(Enum):
    """ Numeric Secondary Type enum"""

    NUM_RIGHT_TAIL = "Num_right_tail"
    NUM_LEFT_TAIL = "Num_left_tail"
    NUM_CENTERED = "Num_centered"


class BooleanSecondaryType(Enum):
    """ Boolean Secondary Type enum """

    FLAG = "Boolean_flag"
    NUMERIC = "Boolean_numeric"


def get_enum_value(v):
    """
    ### Description:

    This function  enum property and return the value of the enum

    ### Args:

    `v`:  an enum object

    """
    if isinstance(v, Enum):
        return v.value
    else:
        return v


class NotificationType(Enum):
    """ Notification type Type enum"""

    SlackWebhook = "SlackWebhook"
    Webhook = "Webhook"
    PagerDuty = "PagerDuty"
    Email = "Email"
    NewRelic = "NewRelic"
    Datadog = "Datadog"


class ScheduleCron(Enum):
    EVERY_DAY_AT_1AM = "0 01 * * *"
    EVERY_DAY_AT_2AM = "0 02 * * *"
    EVERY_DAY_AT_3AM = "0 03 * * *"
    EVERY_DAY_AT_4AM = "0 04 * * *"
    EVERY_DAY_AT_5AM = "0 05 * * *"
    EVERY_DAY_AT_6AM = "0 06 * * *"
    EVERY_DAY_AT_7AM = "0 07 * * *"
    EVERY_DAY_AT_8AM = "0 08 * * *"
    EVERY_DAY_AT_9AM = "0 09 * * *"
    EVERY_DAY_AT_10AM = "0 10 * * *"
    EVERY_DAY_AT_11AM = "0 11 * * *"
    EVERY_DAY_AT_NOON = "0 12 * * *"
    EVERY_DAY_AT_1PM = "0 13 * * *"
    EVERY_DAY_AT_2PM = "0 14 * * *"
    EVERY_DAY_AT_3PM = "0 15 * * *"
    EVERY_DAY_AT_4PM = "0 16 * * *"
    EVERY_DAY_AT_5PM = "0 17 * * *"
    EVERY_DAY_AT_6PM = "0 18 * * *"
    EVERY_DAY_AT_7PM = "0 19 * * *"
    EVERY_DAY_AT_8PM = "0 20 * * *"
    EVERY_DAY_AT_9PM = "0 21 * * *"
    EVERY_DAY_AT_10PM = "0 22 * * *"
    EVERY_DAY_AT_11PM = "0 23 * * *"
    EVERY_DAY_AT_MIDNIGHT = "0 0 * * *"
    EVERY_WEEK = "0 0 * * 0"
    EVERY_WEEKDAY = "0 0 * * 1-5"
    EVERY_WEEKEND = "0 0 * * 6,0"
    EVERY_1ST_DAY_OF_MONTH_AT_MIDNIGHT = "0 0 1 * *"
    EVERY_1ST_DAY_OF_MONTH_AT_NOON = "0 12 1 * *"
    EVERY_2ND_MONTH = "0 0 1 */2 *"
    EVERY_QUARTER = "0 0 1 */3 *"
    EVERY_6_MONTHS = "0 0 1 */6 *"
    EVERY_YEAR = "0 0 1 1 *"
    MONDAY_TO_FRIDAY_AT_1AM = "0 0 01 * * 1-5"
    MONDAY_TO_FRIDAY_AT_2AM = "0 0 02 * * 1-5"
    MONDAY_TO_FRIDAY_AT_3AM = "0 0 03 * * 1-5"
    MONDAY_TO_FRIDAY_AT_4AM = "0 0 04 * * 1-5"
    MONDAY_TO_FRIDAY_AT_5AM = "0 0 05 * * 1-5"
    MONDAY_TO_FRIDAY_AT_6AM = "0 0 06 * * 1-5"
    MONDAY_TO_FRIDAY_AT_7AM = "0 0 07 * * 1-5"
    MONDAY_TO_FRIDAY_AT_8AM = "0 0 08 * * 1-5"
    MONDAY_TO_FRIDAY_AT_9AM = "0 0 09 * * 1-5"
    MONDAY_TO_FRIDAY_AT_09_30AM = "0 30 09 * * 1-5"
    MONDAY_TO_FRIDAY_AT_10AM = "0 0 10 * * 1-5"
    MONDAY_TO_FRIDAY_AT_11AM = "0 0 11 * * 1-5"
    MONDAY_TO_FRIDAY_AT_11_30AM = "0 30 11 * * 1-5"
    MONDAY_TO_FRIDAY_AT_12PM = "0 0 12 * * 1-5"
    MONDAY_TO_FRIDAY_AT_1PM = "0 0 13 * * 1-5"
    MONDAY_TO_FRIDAY_AT_2PM = "0 0 14 * * 1-5"
    MONDAY_TO_FRIDAY_AT_3PM = "0 0 15 * * 1-5"
    MONDAY_TO_FRIDAY_AT_4PM = "0 0 16 * * 1-5"
    MONDAY_TO_FRIDAY_AT_5PM = "0 0 17 * * 1-5"
    MONDAY_TO_FRIDAY_AT_6PM = "0 0 18 * * 1-5"
    MONDAY_TO_FRIDAY_AT_7PM = "0 0 19 * * 1-5"
    MONDAY_TO_FRIDAY_AT_8PM = "0 0 20 * * 1-5"
    MONDAY_TO_FRIDAY_AT_9PM = "0 0 21 * * 1-5"
    MONDAY_TO_FRIDAY_AT_10PM = "0 0 22 * * 1-5"
    MONDAY_TO_FRIDAY_AT_11PM = "0 0 23 * * 1-5"


class NotifyUpon(Enum):
    detection = "detection"
    resolution = "resolution"
    detection_and_resolution = "detection_and_resolution"


class SegmentStatus(Enum):
    __name__ = "SegmentStatus"
    ACTIVE = "ACTIVE"
    ERROR = "ERROR"
    PENDING = "PENDING"
    ARCHIVED = "ARCHIVED"


class SegmentCondition(Enum):
    __name__ = "SegmentCondition"
    GREATER_THAN_EQ = ">="
    LESS_THAN_EQ = "<="
    GREATER_THAN = ">"
    LESS_THAN = "<"
    IS_NULL = "is null"
    IN = "in"
    NOT_IN = "not in"
    EQUALS = "=="
    BETWEEN = "between"


class DatasetType(Enum):
    TRAIN = "Train"
    TEST = "Test"
    VALIDATION = "Validation"
    OTHER = "Other"


class DatasetStatus(Enum):
    FILE_UPLOADED = "file_uploaded"
    INFERRING_DTYPES = "inferring_datatypes"
    INFERRED_DTYPES = "inferred_dtype"
    VALIDATING_DTYPES = "validating_datatypes"
    VALIDATED_DTYPES = "validated_datatypes"
    INFERRING_ROLES = "inferring_roles"
    INFERRED_ROLES = "inferred_roles"
    VALIDATING_ROLES = "validating_roles"
    VALIDATED_ROLES = "validated_roles"
    MATCHING_ENTITIES = "matching_entities"
    ENTITIES_MATCHED = "entities_matched"
    SUMMARIZING = "summarizing"
    SUMMARIZED = "summarized"
    VERSION_CREATED = "version_created"
    UNKNOWN = "unknown"
    FAILED = "failed"
    FULL_FLOW_PROCESSING = "processing"


class DatasetOnFailureOptions(Enum):
    IGNORE = "ignore"
    RAISE = "raise"
