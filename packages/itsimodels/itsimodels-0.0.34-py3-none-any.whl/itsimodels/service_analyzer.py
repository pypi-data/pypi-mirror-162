from itsimodels.core.base_models import BaseModel, ChildModel
from itsimodels.core.fields import (
    BoolField,
    ForeignKey,
    ForeignKeyList,
    ForeignKeyListStr,
    NumberField,
    StringField,
    TypeField, ListField
)

# sample string with multiple keys
# 'e4329258-abd4-4439-b28a-3743b4cda500,fcd637f0-87c5-4a04-a2d5-31cc99ef0dab,...'
# needs to do global search to find all
# this will be the default regex used during key replacement if not provided
MULTIPLE_KEY_RE = r',?([^,]+)'

class TileSettings(ChildModel):
    is_filter_enabled = BoolField(default=False, alias='isFilterEnabled')

    num_tiles = NumberField(default=50, alias='numTiles')


class ServiceAnalyzer(BaseModel):
    key = StringField(required=True, alias='_key')

    title = StringField(required=True)

    description = StringField(default='')

    earliest_time = StringField()

    # this is used in the service analyzer list view filtering. only shows items
    # with isDefault=False
    is_default = BoolField(required=True, default=False, alias='isDefault')

    is_service_filter_enabled = BoolField(alias='isServiceFilterEnabled')

    is_kpi_filter_enabled = BoolField(alias='isKpiFilterEnabled')

    is_tag_filter_enabled = BoolField(alias='isTagFilterEnabled')

    kpi_filter_string = StringField(default='', alias='kpiFilterString')

    kpi_tiles_settings = TypeField(TileSettings, alias='kpiTilesSettings')

    kpi_whitelist = ForeignKeyList(refers='itsimodels.service.Kpi', alias='kpiWhitelist')

    latest_time = StringField()

    search_type = StringField(default='aggregate', alias='searchType')

    service_filter_string = StringField(default='', alias='serviceFilterString')

    service_tiles_settings = TypeField(TileSettings, alias='serviceTilesSettings')

    selected_service_id = ForeignKey(refers='itsimodels.service.Service', alias='selectedServiceId')

    selected_kpi_id = ForeignKey(refers='itsimodels.service.Kpi', alias='selectedKpiId')

    service_white_list = ForeignKeyListStr(refers='itsimodels.service.Service', key_regex=MULTIPLE_KEY_RE, alias='serviceWhitelist')

    show_service_dependencies = BoolField(alias='showServiceDependencies')

    tile_size = StringField(
        choices=('small', 'medium', 'large'),
        default='large',
        alias='tileSize')

    tag_whitelist = StringField(alias='tagWhitelist')

    tag_filter_string = StringField(alias='tagFilterString')

    view = StringField(default='view')

    view_type = StringField(
        choices=('tile', 'topology'),
        default='tile',
        alias='viewType')
