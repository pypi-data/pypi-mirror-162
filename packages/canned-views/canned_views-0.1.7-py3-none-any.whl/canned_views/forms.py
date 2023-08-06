from django import forms
from edc_form_validators import FormValidatorMixin
from edc_sites.forms import SiteModelFormMixin

from .models import CannedView
from .utils import get_sql_view_name_prefix


class CannedViewsForm(SiteModelFormMixin, FormValidatorMixin, forms.ModelForm):

    form_validator_cls = None

    def clean(self):
        super().clean()
        cleaned_data = self.cleaned_data
        if cleaned_data.get("sql_view_name") and not cleaned_data.get(
            "sql_view_name"
        ).startswith(get_sql_view_name_prefix()):
            raise forms.ValidationError(
                {"sql_view_name": f"Invalid. Must start with `{get_sql_view_name_prefix()}`"}
            )
        return cleaned_data

    class Meta:
        model = CannedView
        fields = "__all__"
