from itsimodels.core.base_models import BaseModel, ChildModel
from itsimodels.core.compat import string_types
from itsimodels.core.fields import (
    BoolField,
    DictField,
    ForeignKey,
    ForeignKeyList,
    ForeignKeyMultiEmbeddedStr,
    ListField,
    NumberField,
    StringField,
    TypeField
)


KPI_SUMMARY_RE = r'`get_full_itsi_summary_kpi\((.+)\)`'


KV_STORE_KEY_RE = r'splunk-enterprise-kvstore://(.+)'

'''
Sample urls with object key embedded (one in the middle, one at the end):
Notice Id could belong to multiple types of objects. in below example, 
one is 'savedHomeView', the other is 'service'

/app/itsi/homeview?savedHomeViewId=a8579dde-dac0-11eb-8b20-0a769924fc2e&owner=nobody&view=standard&viewType=service_topology&earliest=-12h&latest=now&serviceId=bb1063f6-56c6-4ea4-8cde-b144b6b9866a&kpiId=e3fb2217f74d9b42292b28a0

/app/itsi/homeview?view=standard&viewType=service_topology&earliest=-12h&latest=now&serviceId=3f4706e8-109e-4af1-9a69-4eab5696c648
'''
EVENT_HANDLER_OPTION_URL_RE = r'Id=([\w-]+?)(?=&|$)'

class ValuedModel(ChildModel):

    def to_dict(self, *args, **kwargs):
        obj = super(ValuedModel, self).to_dict(*args, **kwargs)

        # Remove any null values to conform with the UI visualization library
        data = {key: value for key, value in obj.items() if
                value or (type(value) in (int, float, bool) and value is not None)}

        return data


class DataSourceMeta(ChildModel):
    kpi_id = ForeignKey('itsimodels.service.Kpi', alias='kpiID')

    service_id = ForeignKey('itsimodels.service.Service', alias='serviceID')


class DataSourceOptions(ValuedModel):
    data = DictField()

    # NOTE:
    # glass table --> definition --> data_sources --> options --> query
    # the regex is not complete. ids may have to be manually fixed
    query = ForeignKey('itsimodels.service.Kpi', key_regex=KPI_SUMMARY_RE)

    query_parameters = DictField(alias='queryParameters')


class DataSource(ValuedModel):
    meta = TypeField(DataSourceMeta)

    name = StringField()

    options = TypeField(DataSourceOptions)

    primary = StringField()

    type = StringField()


class DefinitionInput(ChildModel):
    data_sources = DictField(alias='dataSources')

    options = DictField()

    title = StringField()

    type = StringField()


class LayoutImage(ChildModel):
    size_type = StringField(alias='sizeType')

    src = ForeignKey('itsimodels.glass_table_image.GlassTableImage', key_regex=KV_STORE_KEY_RE)

    x = NumberField()

    y = NumberField()


class LayoutOptions(ValuedModel):
    background_color = StringField(alias='backgroundColor')

    background_image = TypeField(LayoutImage, alias='backgroundImage')

    display = StringField()

    height = NumberField()

    show_title_and_description = BoolField(alias='showTitleAndDescription')

    width = NumberField()


class StructureItem(ChildModel):
    # references one of the visualizations id within the
    # glass table definition
    item = StringField()

    position = DictField()

    type = StringField()


class Layout(ChildModel):
    global_inputs = ListField(string_types, alias='globalInputs')

    options = TypeField(LayoutOptions)

    structure = ListField(StructureItem)

    type = StringField()


class VisualizationOptions(ValuedModel):
    # viz.text
    # viz.rectangle
    # viz.area
    # viz.punchcard
    # viz.table
    # viz.img
    # viz.geojson.world
    # splunk.singlevalue

    area_fill_opacity = NumberField(alias='areaFillOpacity')

    axis_titlex_visibility = StringField(alias='axisTitleX__visibility')

    axis_titley_visibility = StringField(alias='axisTitleY__visibility')

    axis_labelsx_major_label_visibility = StringField(alias='axisLabelsX__majorLabelVisibility')

    axis_labelsy_major_label_visibility = StringField(alias='axisLabelsY__majorLabelVisibility')

    background_color = StringField(alias='backgroundColor')

    bubble_color = StringField(alias='bubleColor')

    color = StringField()

    color_mode = StringField(alias='colorMode')

    content = StringField()

    count = NumberField()

    fill = StringField()

    fill_color = StringField(alias='fillColor')

    font_color = StringField(alias='fontColor')

    font_family = StringField(alias='fontFamily')

    font_size = NumberField(alias='fontSize')

    font_weight = StringField(alias='fontWeight')

    foreground_color = StringField(alias='foregroundColor')

    grid_linesx_show_major_lines = BoolField(alias='gridLinesX__showMajorLines')

    grid_linesy_show_major_lines = BoolField(alias='gridLinesY__showMajorLines')

    legend_placement = StringField(alias='legend__placement')

    logical_bounds = DictField(alias='logicalBounds')

    icon = ForeignKey('itsimodels.glass_table_icon.GlassTableIcon', key_regex=KV_STORE_KEY_RE)

    major_font_size = NumberField(alias='majorFontSize')

    major_color = StringField(alias='majorColor')
    
    major_value = StringField(alias='majorValue')

    name = StringField()

    number_precision = NumberField(alias='numberPrecision')

    projection = StringField()

    preserve_aspect_ratio = BoolField(alias='preserveAspectRatio')

    rotation = NumberField()

    row_background_color_even = StringField(alias='rowBackgroundColorEven')

    row_background_color_odd = StringField(alias='rowBackgroundColorOdd')

    row_text_color_even = StringField(alias='rowTextColorOdd')

    row_text_color_odd = StringField(alias='rowTextColorEven')

    rx = NumberField()

    ry = NumberField()

    selector = StringField()

    series_colors = ListField(alias='seriesColors')

    show_bubble_labels = StringField(alias='showBubbleLabels')

    show_max_value_pulsation = BoolField(alias='showMaxValuePulsation')

    show_trend_indicator = BoolField(alias='showTrendIndicator')

    show_spark_line = BoolField(alias='showSparkline')

    show_spark_line_tooltip = BoolField(alias='showSparklineTooltip')

    show_value = BoolField(alias='showValue')

    source = StringField()

    source_bounds = DictField(alias='sourceBounds')

    spark_line_display = StringField(alias='sparklineDisplay')

    spark_line_position = StringField(alias='sparklinePosition')

    spark_line_stroke_color = StringField(alias='sparklineStrokeColor')

    spark_line_values = StringField(alias='sparklineValues')

    src = ForeignKey('itsimodels.glass_table_image.GlassTableImage', key_regex=KV_STORE_KEY_RE)

    stroke = StringField()

    stroke_width = NumberField(alias='strokeWidth')

    stroke_color = StringField(alias='strokeColor')

    stroke_highlight_color = StringField(alias='strokeHighlightColor')

    text_color = StringField(alias='textColor')
    
    trend_color = StringField(alias='trendColor')

    trend_display = StringField(alias='trendDisplay')

    trend_display_mode = StringField(alias='trendDisplayMode')

    trend_value = StringField(alias='trendValue')

    unit = StringField()

    unit_position = StringField(alias='unitPosition')

    width = NumberField()


class EventHandlerOption(ValuedModel):
    key = StringField()

    newTab = BoolField()

    type = StringField()

    # None refers because we want to check all types of objects for key
    # mapping. It is because the object key embeded could belong to different
    # types, not just one (see example above regarding EVENT_HANDLER_OPTION_URL_RE
    url = ForeignKeyMultiEmbeddedStr(refers=None, key_regex=EVENT_HANDLER_OPTION_URL_RE)


class EventHandlers(ChildModel):
    options = TypeField(EventHandlerOption)

    type = StringField()


class Visualization(ValuedModel):
    data_sources = DictField(alias='dataSources')

    encoding = DictField()

    event_handlers = ListField(EventHandlers, alias='eventHandlers')

    options = TypeField(VisualizationOptions)

    # references visualization ids within glass table def
    primary = StringField()

    title = StringField()

    type = StringField()

    context = DictField()


class Definition(ChildModel):
    data_sources = DictField(DataSource, alias='dataSources')

    defaults = DictField()

    description = StringField()

    inputs = DictField(DefinitionInput)

    layout = TypeField(Layout)

    title = StringField()

    visualizations = DictField(Visualization)


class GlassTable(BaseModel):
    key = StringField(required=True, alias='_key')

    title = StringField(required=True)

    definition = TypeField(Definition)

    description = StringField(default='')

    gt_version = StringField(default='beta')

    # interactable = BoolField()

    latest = StringField(default='now')

    latest_label = StringField(default='Now')

    swap_service_ids = ForeignKeyList('itsimodels.service.Service')

    selected_swap_service_id = ForeignKey('itsimodels.service.Service')

    template_selected_service_id = ForeignKey('itsimodels.service.Service', alias='templateSelectedServiceId')

    template_swappable_service_ids = ForeignKeyList('itsimodels.service.Service', alias='templateSwappableServiceIds')

