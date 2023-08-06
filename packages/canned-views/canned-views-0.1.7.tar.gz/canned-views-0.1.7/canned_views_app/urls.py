from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from edc_auth.views import LogoutView
from edc_dashboard.utils import get_index_page
from edc_dashboard.views import AdministrationView
from edc_utils.paths_for_urlpatterns import paths_for_urlpatterns

from .views import HomeView

app_name = "canned_views_app"

urlpatterns = [
    path("accounts/", include("edc_auth.urls")),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    *paths_for_urlpatterns("edc_dashboard"),
    *paths_for_urlpatterns("edc_export"),
    *paths_for_urlpatterns("edc_randomization"),
    *paths_for_urlpatterns("edc_notification"),
    *paths_for_urlpatterns("canned_views"),
    path("admin/", admin.site.urls),
    path(
        "switch_sites/",
        LogoutView.as_view(next_page=get_index_page()),
        name="switch_sites_url",
    ),
    path("home/", HomeView.as_view(), name="home_url"),
    re_path(".", RedirectView.as_view(url="/"), name="home_url"),
    re_path("", HomeView.as_view(), name="home_url"),
]
