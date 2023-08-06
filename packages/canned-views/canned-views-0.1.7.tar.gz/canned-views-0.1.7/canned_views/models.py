from django.core.validators import RegexValidator
from django.db import models
from edc_constants.choices import YES_NO
from edc_constants.constants import NO
from edc_model.models import BaseUuidModel, HistoricalRecords
from edc_sites.models import CurrentSiteManager, SiteModelMixin
from edc_utils import get_utcnow


class CannedView(SiteModelMixin, BaseUuidModel):

    report_datetime = models.DateTimeField(default=get_utcnow)

    name = models.CharField(max_length=30, validators=[RegexValidator(regex="^([a-z0-9_])+$")])

    display_name = models.CharField(max_length=50, blank=True)

    description = models.TextField(
        null=True,
        blank=True,
        help_text=(
            "Appears in the report header. A clear "
            "descrtiption of the report and its intended use."
        ),
    )

    instructions = models.TextField(
        null=True,
        blank=True,
        help_text="Appears in the report header. Instructions for the user of the report",
    )

    sql_view_name = models.CharField(
        max_length=50,
        null=True,
        blank=False,
        validators=[RegexValidator(regex="^([a-z0-9_])+$")],
    )

    sql_select_columns = models.TextField(
        null=True,
        blank=True,
        validators=[RegexValidator(regex="^([a-z0-9_, ])+$")],
        help_text="Comma separated list of field names for the " "SQL SELECT. All lowercase",
    )

    filter_by_current_site = models.CharField(
        max_length=10,
        choices=YES_NO,
        default=NO,
        help_text="If yes, the column `site_id` is expected",
    )

    reverse_url = models.CharField(max_length=10, choices=YES_NO, default=NO)

    linked_column_name = models.CharField(max_length=50, default="subject_identifier")

    reverse_url_name = models.CharField(
        max_length=50,
        null=True,
        help_text=(
            "a valid url name as a `key` for the `value` stored in the `url_names` "
            "dictionary. For example, `subject_dashboard_url`."
        ),
    )

    reverse_url_args = models.CharField(
        max_length=500,
        null=True,
        help_text=(
            "column names separated by comma. For example, "
            "subject_identifier,visit_code,visit_code_sequence,"
            "visit_schedule_name,schedule_name."
        ),
    )

    objects = models.Manager()

    history = HistoricalRecords()

    sites = CurrentSiteManager()

    def __str__(self):
        return self.name

    class Meta(BaseUuidModel.Meta):
        verbose_name = "Canned View"
        verbose_name_plural = "Canned Views"
