import re

from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django.views.generic import ListView
from edc_constants.constants import YES
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin

from ..models import CannedView
from ..utils import DynamicModel, DynamicModelError


class CannedViewNameError(Exception):
    pass


class BasicView(EdcViewMixin, NavbarViewMixin, ListView):
    queryset = None
    paginate_by = 300
    template_name = "canned_views/canned_view.html"  # noqa
    navbar_selected_item = "canned_views"

    def __init__(self, **kwargs):
        self.report_definition = None
        super().__init__(**kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_url = reverse("canned_views_admin:canned_views_cannedview_changelist")
        context.update(
            admin_url=f"{admin_url}?q={self.report_definition.name}",
            report_definition=self.report_definition,
        )
        return context

    def get(self, request, *args, selected_report_name=None, **kwargs):
        try:
            self.report_definition = CannedView.objects.get(name=selected_report_name)
        except ObjectDoesNotExist as e:
            raise CannedViewNameError(e)
        try:
            dynamic_model = DynamicModel(**self.report_definition.__dict__)
        except DynamicModelError as e:
            raise CannedViewNameError(e)
        self.model = dynamic_model.model_cls
        sql = dynamic_model.get_sql(self.report_definition.sql_select_columns)
        if self.report_definition.filter_by_current_site == YES:
            if self.site_id and re.match(r"^\w+$", f"{self.site_id}"):
                sql = f"{sql} where site_id={self.site_id}"
        self.queryset = self.model.objects.raw(sql)
        return super().get(request, *args, **kwargs)

    @property
    def site_id(self):
        try:
            return self.request.site.id  # noqa
        except AttributeError:
            return None
