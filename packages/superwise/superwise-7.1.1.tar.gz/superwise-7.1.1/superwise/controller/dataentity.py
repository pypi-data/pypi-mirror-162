""" This module implements data entities functionality """
import pandas as pd

from superwise.config import Config
from superwise.controller.base import BaseController
from superwise.utils.exceptions import SuperwiseUnsupportedException
from superwise.utils.exceptions import SuperwiseValidationException
from superwise.controller.infer import infer_dtype
from superwise.controller.summary.entities_validator import EntitiesValidator
from superwise.controller.summary.feature_importance import FeatureImportance
from superwise.controller.summary.summary import Summary
from superwise.models.data_entity import DataEntity
from superwise.models.data_entity import DataEntitySummary
from superwise.resources.superwise_enums import get_enum_value


class DataEntityController(BaseController):
    """ controller for Data entities  """

    def __init__(self, client, sw):
        """


        ### Args:

        `client`: client object

        `sw`: superwise object

        """
        super().__init__(client, sw)
        self.path = "model/v1/data_entities"
        self.model_name = "DataEntity"
        self._entities_df = None
        self.data = None

    @staticmethod
    def _pre_process_data(data):
        data.columns = data.columns.str.lower()
        for column in Config.LIST_DROP_DATA_COLS:
            if column in data.columns:
                data = data.drop(column, axis=1)
        return data

    def create(self, name=None, type=None, dimension_start_ts=None, role=None, feature_importance=None):
        """
        ### Description:

         create dataentity

        ### Args:

        `name`: name for dataentity

        `type`:

        `dimension_start_ts`:

        `role`: role of dataentity (DataEntityRole)

        `feature_importance`: feature importance value

        """

        params = locals()
        return self._dict_to_model(params)

    def update_summary(self, data_entity_id, summary):
        """
        ### Description:

        update summary implementation
        """
        self.model = DataEntitySummary(data_entity_id, summary)
        self.model_name = "DataEntitySummary"
        self.create(self.model)

    def generate_summary(self, data_entities, model, data, base_version=None, **kwargs):
        """
        ### Description:
        Unsupported anymore, this function raise Exception
        """
        raise SuperwiseUnsupportedException(
            "Unsupported SDK API, please use  summarise() instead," " See CHANGELOG for more details"
        )

    def summarise(
        self,
        data,
        specific_roles,
        default_role="feature",
        entities_dtypes=None,
        importance_mapping=None,
        importance_target_label=None,
        importance_sample=None,
        base_version=None,
        **kwargs
    ):
        """
        ### Description:
        Summarise the baseline data

        ### Args:

        `data`: a dataframe of baseline data

        `entities_dtypes`: ndtypes dictionary or None for auto infer internally

            HOW TO USE OPTIONS:

            - Manually create dictionary as:
                  {"feature_0" : "Boolean",
                "feature_1" : "Categorical"
                }

            -  run infer to get dictionary and pass the value to allow override of infer results:
                from superwise.controller.infer import infer_dtype
                dtypes = infer_dtypes(baseline_df)

            - pass None
                the summarise function will auto generate the dtypes.

        `specific_roles`: dictionary of roles, for example:

            {"feature_1" : "feature",
             "record_id" : "id"}

        `default_role`: a default role used by SDK (normally and by default is feature)

        `importance_mapping`: mapping dictionary for feature importance, example:

            {"feature_0" : 0.4}


        `importance_target_label`: option to specifics a label target for feature importance

        `importance_sample`: allow sampling of data for feature importance.
                this option should be used for big baseline data

        `base_version`:  base version. useful to inherit information from already exist version

        ### Return:

        list of DataEntity objects.
        """
        if not entities_dtypes:
            entities_dtypes = infer_dtype(data)
        entities_dtypes = dict((k.lower(), v) for k, v in entities_dtypes.items())
        for key in specific_roles:
            specific_roles[key] = get_enum_value(specific_roles[key])

        self.data = self._pre_process_data(data)
        data_entities = []
        for entity in entities_dtypes:
            importance_value = importance_mapping.get(entity, None) if importance_mapping else None
            data_entities.append(
                {
                    "name": entity,
                    "role": specific_roles.get(entity, default_role),
                    "type": entities_dtypes[entity],
                    "feature_importance": importance_value,
                    "dimension_start_ts": None,
                    "id": None,
                }
            )

        if base_version:
            if base_version.status not in ["Pending", "Active"]:
                raise SuperwiseValidationException(
                    "base version should be used for summarized only version, current status: {}".format(
                        base_version.status
                    )
                )
            r = self.client.get(self.client.build_url("model/v1/versions/{}/data_entities".format(base_version.id)))
            previous_entities = self.parse_response(r, is_return_model=False)
            previous_entities = [e["data_entity"] for e in previous_entities]
            previous_entities_dict = {}
            if previous_entities:
                for data_entity in previous_entities:
                    previous_entities_dict[data_entity["name"]] = data_entity["id"]
            for de in data_entities:
                if de["name"] in previous_entities_dict:
                    de["id"] = previous_entities_dict[de["name"]]
                else:
                    de["id"] = None

        entities_df = pd.DataFrame(data_entities)
        self._entities_df = entities_df
        validator = EntitiesValidator(entities_df, self.data)

        self.data = validator.prepare()
        if not importance_mapping:
            fi = FeatureImportance(self._entities_df)
            self._entities_df = fi.compute(self.data, target=importance_target_label, sample=importance_sample)
        entities_df_summary = Summary(self._entities_df, self.data).generate()
        data_entities = DataEntity.df_to_list(entities_df_summary)
        return data_entities
