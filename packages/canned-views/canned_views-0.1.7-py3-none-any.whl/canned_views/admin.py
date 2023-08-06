from django.contrib import admin
from django.template.loader import render_to_string
from django.urls import reverse

from .admin_site import canned_views_admin
from .auth_objects import CANNED_VIEW_SUPER_ROLE
from .forms import CannedViewsForm
from .models import CannedView


@admin.register(CannedView, site=canned_views_admin)
class CannedViewAdmin(admin.ModelAdmin):

    form = CannedViewsForm

    fieldsets = (
        (
            None,
            (
                {
                    "fields": (
                        "report_datetime",
                        "name",
                        "display_name",
                        "description",
                        "instructions",
                        "sql_view_name",
                        "sql_select_columns",
                        "filter_by_current_site",
                    )
                }
            ),
        ),
        (
            "Custom url",
            (
                {
                    "fields": (
                        "reverse_url",
                        "linked_column_name",
                        "reverse_url_name",
                        "reverse_url_args",
                    )
                }
            ),
        ),
    )

    list_display = [
        "display_name",
        "list_view",
        "description",
        "sql_view_name",
    ]

    search_fields = ("name", "display_name", "sql_view_name")

    readonly_fields = ("sql_view_name", "sql_select_columns")

    def get_readonly_fields(self, request, obj=None) -> tuple:
        readonly_fields = super().get_readonly_fields(request, obj=obj) or ()
        try:
            roles = request.user.userprofile.roles.all()
        except AttributeError:
            pass
        else:
            role_names = tuple(role.name for role in roles)
            if "sql_view_name" in readonly_fields and CANNED_VIEW_SUPER_ROLE in role_names:
                readonly_fields = tuple(
                    f
                    for f in readonly_fields
                    if f not in ("sql_view_name", "sql_select_columns")
                )
        return readonly_fields

    @staticmethod
    def list_view(obj=None, label=None):
        url = reverse(
            "canned_views:basic_view_url",
            kwargs=dict(selected_report_name=obj.name),
        )
        context = dict(title="Go to canned view", url=url, label=label)
        return render_to_string("canned_views/button.html", context=context)
