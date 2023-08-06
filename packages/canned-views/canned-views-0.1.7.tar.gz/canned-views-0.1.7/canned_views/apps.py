from django.apps import AppConfig as DjangoAppConfig


class AppConfig(DjangoAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "canned_views"
    verbose_name = "Canned Views"
    has_exportable_data = True
    include_in_administration_section = True
