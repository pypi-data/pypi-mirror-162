from itsimodels.core.base_models import BaseModel, ChildModel
from itsimodels.core.compat import string_types
from itsimodels.core.fields import (
    BoolField,
    DictField,
    ForeignKey,
    ForeignKeyList,
    ListField,
    NumberField,
    StringField,
    TypeField, ForeignKeyMultiEmbeddedStr
)
from itsimodels.team import GLOBAL_TEAM_KEY


'''
Many searches in kip embeds various ids in the query string
we attempt to capture most of them. notice the matching/replacement happens
in itsicli.content_packs.backup.KeysUpdater
'''
GENERIC_SEARCH_RE = (r'id *= *\\"([\w-]+?)(?= |\\)|'             # i.e. serviceid=\"a5d84252-acec-40a4-bf1f-ba6f2aecc6ce\"
                     r'id *= *([\w-]+?)(?= |$)|'                   # i.e. kpi_id=fcdce583cea75e75d5e26e7d
                     r'`assess_severity\(([\w-]+?) *, *([\w-]+?)\)`|' # i.e. `assess_severity(a5d84252-acec-40a4-bf1f-ba6f2aecc6ce, fcdce583cea75e75d5e26e7d)`
                     r'`assess_severity\(([\w-]+?) *, *([\w-]+?) *,.+?\)`|'   # i.e. `assess_severity(a5d84252-acec-40a4-bf1f-ba6f2aecc6ce, fcdce583cea75e75d5e26e7d ,  true, true, true)`
                     r'`get_full_itsi_summary_[\w]+?\(([\w-]+?)\)`') # i.e. `get_full_itsi_summary_service_health_events(4dbc2a97-8d0e-4b29-92db-2cc5d426a71f)`

class ThresholdLevel(ChildModel):

    dynamic_param = NumberField(alias='dynamicParam')

    severity_color = StringField(alias='severityColor')

    severity_color_light = StringField(alias='severityColorLight')

    severity_label = StringField(alias='severityLabel')

    severity_label_localized = StringField(alias='severityLabelLocalized')

    severity_value = NumberField(alias='severityValue')

    threshold_value = NumberField(alias='thresholdValue')




class KpiThresholds(ChildModel):
    base_severity_color = StringField(alias='baseSeverityColor')

    base_severity_color_light = StringField(alias='baseSeverityColorLight')

    base_severity_label = StringField(default='info', alias='baseSeverityLabel')

    base_severity_value = NumberField(alias='baseSeverityValue')

    gauge_max = NumberField(default=100, alias='gaugeMax')

    gauge_min = NumberField(default=0, alias='gaugeMin')

    is_max_static = BoolField(default=False, alias='isMaxStatic')

    is_min_static = BoolField(default=False, alias='isMinStatic')

    metric_field = StringField(alias='metricField')

    render_boundary_max = NumberField(alias='renderBoundaryMax')

    render_boundary_min = NumberField(alias='renderBoundaryMin')

    threshold_levels = ListField(ThresholdLevel, alias='thresholdLevels')


class KpiTimePolicy(ChildModel):
    title = StringField(required=True)

    aggregate_thresholds = TypeField(KpiThresholds)

    entity_thresholds = TypeField(KpiThresholds)

    policy_type = StringField(default='static')

    time_blocks = ListField(object)


class KpiTimePolicies(ChildModel):
    policies = DictField(KpiTimePolicy)


class MetricSearchSpec(ChildModel):
    metric_index = StringField(default='')

    metric_name = StringField(default='')


class DatamodelFilter(ChildModel):

    field = StringField(alias='_field')

    operator = StringField(alias='_operator')

    value = StringField(alias='_value')


class DatamodelSearchSpec(ChildModel):
    datamodel = StringField()

    object = StringField()

    field = StringField()

    owner_field = StringField()


class Kpi(ChildModel):
    key = StringField(required=True, alias='_key')

    title = StringField(required=True)

    alert_eval = StringField()

    aggregate_eval = StringField()

    aggregate_statop = StringField(default='avg')

    adaptive_thresholding_training_window = StringField()

    adaptive_thresholds_is_enabled = BoolField(default=False)

    aggregate_thresholds = TypeField(KpiThresholds)

    aggregate_thresholds_alert_enabled = BoolField(default=False)

    aggregate_thresholds_custom_alert_enabled = BoolField(default=False)

    aggregate_thresholds_custom_alert_rules = ListField()

    alert_lag = StringField(default='30')

    alert_on = StringField()

    alert_period = StringField()

    anomaly_detection_alerting_enabled = BoolField(default=False)

    anomaly_detection_is_enabled = BoolField(default=False)

    anomaly_detection_sensitivity = NumberField()

    anomaly_detection_training_window = StringField()

    aggregate_threshold_alert_enabled = BoolField(default=False)

    backfill_earliest_time = StringField(default='-7d')

    backfill_enabled = BoolField(default=False)

    base_search = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    base_search_id = ForeignKey('itsimodels.kpi_base_search.KpiBaseSearch')

    base_search_metric = ForeignKey('itsimodels.kpi_base_search.SearchMetric')

    cohesive_ad = DictField()

    cohesive_anomaly_detection_is_enabled = BoolField(default=False)

    datamodel = TypeField(DatamodelSearchSpec)

    datamodel_filter = ListField(DatamodelFilter)

    datamodel_filter_clauses = StringField()

    description = StringField(default='')

    enabled = BoolField(default=False)

    entity_filter_field = StringField(default='', alias='entity_id_fields')

    entity_split_field = StringField(default='', alias='entity_breakdown_id_fields')

    entity_statop = StringField(default='avg')

    entity_thresholds = TypeField(KpiThresholds)

    fill_gaps = StringField(default='null_value')

    gap_custom_alert_value = NumberField()

    gap_severity = StringField(default='unknown')

    gap_severity_color = StringField(default='')

    gap_severity_color_light = StringField(default='')

    gap_severity_value = StringField(default='-1')

    kpi_base_search = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    kpi_template_kpi_id = ForeignKey('itsimodels.kpi_threshold_template.KpiThresholdTemplate')

    kpi_threshold_template_id = ForeignKey('itsimodels.kpi_threshold_template.KpiThresholdTemplate')

    is_filter_entities_to_service = BoolField(default=False, alias='is_service_entity_filter')

    is_split_by_entity = BoolField(default=False, alias='is_entity_breakdown')

    metric_search_spec = TypeField(MetricSearchSpec, alias='metric')

    metric_qualifier = StringField()

    search = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_aggregate = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_alert = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_alert_earliest = StringField()

    search_alert_entities = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_buckets = StringField()

    search_entities = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_occurrences = NumberField()

    search_time_compare = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_time_series = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_time_series_aggregate = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_time_series_entities = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=GENERIC_SEARCH_RE)

    search_type = StringField(default='adhoc')

    service_title = StringField()

    threshold_eval = StringField()

    threshold_field = StringField(default='')

    time_policies = TypeField(KpiTimePolicies, alias='time_variate_thresholds_specification')

    trending_ad = DictField()

    type = StringField(default='kpis_primary')

    tz_offset = StringField()

    unit = StringField(default='')

    use_time_policies = BoolField(default=False, alias='time_variate_thresholds')

    urgency = NumberField()


class EntityRuleItem(ChildModel):
    field = StringField()

    field_type = StringField()

    rule_type = StringField()

    value = StringField()


class EntityRule(ChildModel):
    rule_condition = StringField()

    rule_items = ListField(EntityRuleItem)


class ServiceDependency(ChildModel):
    kpis_depending_on = ForeignKeyList('itsimodels.service.Kpi')

    service_id = ForeignKey('itsimodels.service.Service', alias='serviceid')


class ServiceTags(ChildModel):
    tags = ListField(string_types)

    template_tags = ListField(string_types)


class Service(BaseModel):
    key = StringField(required=True, alias='_key')

    algorithms = DictField()

    title = StringField(required=True)

    description = StringField(default='')

    enabled = BoolField(default=False)

    entity_rules = ListField(EntityRule)

    kpis = ListField(Kpi)

    services_depends_on = ListField(ServiceDependency)

    services_depending_on_me = ListField(ServiceDependency)

    service_template_id = ForeignKey('itsimodels.service_template.ServiceTemplate', alias='base_service_template_id')

    service_tags = TypeField(ServiceTags)

    team_id = ForeignKey('itsimodels.team.Team', default=GLOBAL_TEAM_KEY, alias='sec_grp')
