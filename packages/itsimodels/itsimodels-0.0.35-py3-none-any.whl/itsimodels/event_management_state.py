from itsimodels.core.base_models import BaseModel, ChildModel
from itsimodels.core.fields import BoolField, DictField, ForeignKeyMultiEmbeddedStr, ListField, NumberField, StringField


# Regex defined to parse the list of supported policies: "\"cef5eec4-2dcc-11eb-8ffb-0671d5072164\",\"e3ec489a-04b1-11ea-8567-021bca2da03d\",\"48a35d46-0557-11ea-9716-021bca2da03d\",\"76073f1c-303c-11eb-8ffe-0671d5072164\""
GENERIC_POLICY_RE = r'"([\w-]+?)"'


class FilterSpecification(ChildModel):
    id = StringField()

    label = StringField()

    text = StringField()

    value = ForeignKeyMultiEmbeddedStr(
        refers=None, key_regex=GENERIC_POLICY_RE)


class EventManagementState(BaseModel):
    key = StringField(required=True, alias='_key')

    title = StringField(required=True)

    arbitrary_search = StringField(alias='arbitrarySearch')

    auto_refresh = NumberField(alias='autoRefresh')

    columns_shown = ListField(object, alias='columnsShown')

    configured_tab_id = StringField(alias='configuredTabId')

    dashboard = StringField()

    description = StringField()

    earliest = StringField()

    event_deduplication = BoolField(alias='eventDeduplication')

    event_deduplication_field = StringField(alias='eventDeduplicationField')

    event_field_filter = DictField(alias='eventFieldFilter')

    fetch_limit = NumberField(alias='fetchLimit')

    filter_collection = ListField(
        FilterSpecification, alias='filterCollection')

    identifying_name = StringField()

    interactable = BoolField()

    latest = StringField()

    show_summary_dashboard = BoolField(alias='showSummaryDashboard')

    sort_direction = StringField(alias='sortDirection')

    sort_field = StringField(alias='sortField')

    view_mode = StringField(alias='viewMode')

    viewing_option = StringField(alias='viewingOption')
