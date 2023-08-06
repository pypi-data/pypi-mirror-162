from edc_model_admin.admin_site import EdcAdminSite

from .apps import AppConfig

canned_views_admin = EdcAdminSite(name="canned_views_admin", app_label=AppConfig.name)
