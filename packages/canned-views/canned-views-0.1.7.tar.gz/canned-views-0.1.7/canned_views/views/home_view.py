from django.conf import settings
from django.urls import reverse
from django.views.generic import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin, UrlRequestContextMixin
from edc_navbar import NavbarViewMixin

from canned_views.models import CannedView


class HomeView(UrlRequestContextMixin, EdcViewMixin, NavbarViewMixin, TemplateView):

    navbar_selected_item = "canned_views_home"
    template_name = "canned_views/home.html"  # noqa
    url_name = "home_url"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        reports = CannedView.objects.all().order_by("name")
        home_url = reverse(self.get_home_url_name())
        context.update(reports=reports, home_url=home_url)
        return context

    def get_home_url_name(self):
        if "edc_data_manager" in [x.split(".")[0] for x in settings.INSTALLED_APPS]:
            return "edc_data_manager:home_url"
        return self.url_name
