from django.conf import settings
from django.views.generic import TemplateView
from edc_dashboard.view_mixins import EdcViewMixin
from edc_navbar import NavbarViewMixin


class HomeView(EdcViewMixin, NavbarViewMixin, TemplateView):
    template_name = f"{settings.APP_NAME}/home.html"
    navbar_name = "canned_views_app"
    navbar_selected_item = "home"
