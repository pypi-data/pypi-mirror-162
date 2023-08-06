from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "canned_views_app"
    verbose_name = "Reports"
    default_navbar_name = "canned_views_app"
