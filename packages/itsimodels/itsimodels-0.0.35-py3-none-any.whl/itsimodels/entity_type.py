from itsimodels.core.base_models import (
    BaseModel,
    ChildModel
)
from itsimodels.core.compat import string_types
from itsimodels.core.fields import (
    DictField,
    ListField,
    StringField,
    TypeField, NumberField, ForeignKeyMultiEmbeddedStr
)
from itsimodels.service import GENERIC_SEARCH_RE


class DataDrilldown(ChildModel):
    title = StringField(required=True)

    type = StringField(required=True)

    entity_field_filter = DictField(object)

    static_filter = DictField(object)


class DashboardDrilldownParams(ChildModel):
    alias_param_map = ListField(object)

    static_params = DictField(object)


class DashboardDrilldown(ChildModel):
    title = StringField(required=True)

    id = StringField(required=True)

    dashboard_type = StringField(required=True)

    base_url = StringField(default='')

    params = TypeField(DashboardDrilldownParams)


class VitalMetric(ChildModel):
    metric_name = StringField(required=True)

    search = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    is_key = NumberField(default=0)

    matching_entity_fields = ListField(string_types)

    split_by_fields = ListField(string_types)

    unit = StringField(default='')


class EntityType(BaseModel):
    key = StringField(required=True, alias='_key')

    title = StringField(required=True)

    description = StringField(default='')

    vital_metrics = ListField(VitalMetric)

    data_drilldowns = ListField(DataDrilldown)

    dashboard_drilldowns = ListField(DashboardDrilldown)
