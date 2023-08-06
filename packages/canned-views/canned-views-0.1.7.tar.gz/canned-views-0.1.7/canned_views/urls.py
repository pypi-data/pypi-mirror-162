from django.urls.conf import path, re_path

from .views import BasicView, HomeView

app_name = "canned_views"

urlpatterns = [
    re_path(
        "canned_views/(?P<selected_report_name>[a-z0-9_]+)/$",
        BasicView.as_view(),
        name="basic_view_url",
    ),
    path("", HomeView.as_view(), name="home_url"),
]
