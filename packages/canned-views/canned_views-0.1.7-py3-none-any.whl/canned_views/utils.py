from typing import Any, List, Optional

import sqlvalidator
from django import forms
from django.conf import settings
from django.db import OperationalError, connection, models

from .constants import BAD_CHARS


class DynamicModelError(Exception):
    pass


def get_sql_view_name_prefix():
    return getattr(settings, "CANNED_VIEWS_PREFIX", "canned_")


def validated_sql_select(sql_select):
    bad_words = ["insert", "delete", "update", "create", "alter"]
    if sql_select:
        sql_select = sql_select.lower()
        if sql_select.strip(BAD_CHARS) != sql_select:
            raise forms.ValidationError(
                {"sql_select": "Invalid SQL select statement. Bad char"}
            )
        for word in bad_words:
            if word in sql_select:
                raise forms.ValidationError(
                    {"sql_select": f"Invalid SQL select statement. Bad word. Got {word}"}
                )
        sql_query = sqlvalidator.parse(sql_select)
        if not sql_query.is_valid():
            raise forms.ValidationError(
                {"sql_select": "Invalid SQL statement. Statement did not validate."}
            )
    return sql_select


class Dialect:
    def __init__(self, field_attr, type_attr):
        self.field = field_attr
        self.type = type_attr


Dialects = dict(mysql=Dialect("Field", "Type"), sqlite=Dialect("name", "type"))


class DynamicModel:
    def __init__(
        self,
        name: Optional[str] = None,
        sql_view_name: Optional[str] = None,
        reverse_url: Optional[str] = None,
        reverse_url_name: Optional[str] = None,
        reverse_url_args: Optional[str] = None,
        filter_by_current_site: Optional[str] = None,
        **kwargs,  # noqa
    ):
        self._attrs = {}
        self.sql_select_columns = []
        self.sql_describe: Optional[str] = None
        self.dialect: Optional[Dialect] = None
        self.columns: Optional[List[str]] = None
        self.reverse_url = reverse_url
        self.reverse_url_name = reverse_url_name
        self.reverse_url_args = reverse_url_args
        self.filter_by_current_site = filter_by_current_site
        if name != name.replace(" ", "").lower().strip(BAD_CHARS):
            raise DynamicModelError("Invalid report name")
        if sql_view_name != sql_view_name.replace(" ", "").lower().strip(BAD_CHARS):
            raise DynamicModelError("Invalid sql_view_name")
        if not sql_view_name.startswith(get_sql_view_name_prefix()):
            raise DynamicModelError(
                f"Invalid sql_view_name. Must start with `{get_sql_view_name_prefix()}`"
            )
        self.sql_view_name = sql_view_name
        self.read_from_cursor()
        model_name = f"TemporaryView{name.replace('_', '').lower().title()}"
        # create class
        self.model_cls = type(model_name, (models.Model,), self.model_attrs)
        # unregister from all_models
        try:
            del self.model_cls._meta.apps.all_models[settings.APP_NAME][  # noqa
                model_name.lower()
            ]
        except KeyError:
            pass

    def get_sql(self, cols: Optional[str] = None):
        cols = cols.replace(" ", "").split(",") if cols else []
        for col in cols:
            if col not in self.sql_select_columns:
                raise DynamicModelError(f"Invalid column specified. Got `{col}`.")
        sql_select_columns = cols or self.sql_select_columns
        # if self.reverse_url == YES:
        #     args = tuple() if self.reverse_url_args is None else
        #     url_name = url_names.get(self.reverse_url_name)
        #     sql_select_columns.append(f"'{url_name}' as url")
        # if "subject_identifier" in sql_select_columns and "url" not in sql_select_columns:
        #     url_name = url_names.get("subject_dashboard_url")
        #     sql_select_columns.append(f"'{url_name}' as url")
        if "id" not in sql_select_columns:
            sql = f"select {','.join(sql_select_columns)}, 0 AS id from {self.sql_view_name}"
        else:
            sql = f"select {','.join(sql_select_columns)} from {self.sql_view_name}"
        return sql

    def read_from_cursor(self):
        """Determine server type and update select command and column names."""
        with connection.cursor() as cursor:
            try:
                cursor.execute(f"describe {self.sql_view_name}")
            except OperationalError:
                cursor.execute(f"select * from pragma_table_info('{self.sql_view_name}')")
                self.sql_describe = f"select * from pragma_table_info('{self.sql_view_name}')"
                self.dialect = Dialects.get("sqlite")
            else:
                self.sql_describe = f"describe {self.sql_view_name}"
                self.dialect = Dialects.get("mysql")
            self.columns = [col[0] for col in cursor.description]

    @property
    def model_attrs(self) -> dict:
        """Returns dict of model attrs -- field classes, etc"""
        attrs = {}
        with connection.cursor() as cursor:
            cursor.execute(self.sql_describe)
            for row in cursor.fetchall():
                rowdict = dict(zip(self.columns, row))
                self.sql_select_columns.append(rowdict.get(self.dialect.field))
                attrs.update(
                    {
                        rowdict.get(self.dialect.field): self.get_dynamic_field_cls(
                            rowdict.get(self.dialect.type)
                        ),
                    }
                )
            attrs.update({"__module__": f"{settings.APP_NAME}.models"})
        return attrs

    @staticmethod
    def get_dynamic_field_cls(field_type: str) -> Any:
        field_type = field_type.lower()
        if field_type.startswith("varchar"):
            max_length = int(field_type.replace("varchar(", "").split(")")[0])
            field_cls = models.CharField(max_length=max_length, null=True)
        elif field_type.startswith("char"):
            max_length = int(field_type.replace("char(", "").split(")")[0])
            field_cls = models.CharField(max_length=max_length, null=True)
        elif field_type.startswith("text") or field_type.startswith("longtext"):
            field_cls = models.TextField(null=True)
        elif (
            field_type.startswith("integer")
            or field_type.startswith("int")
            or field_type.startswith("bigint")
            or field_type.startswith("tinyint")
        ):
            field_cls = models.IntegerField(null=True)
        elif field_type.startswith("datetime"):
            field_cls = models.DateTimeField(null=True)
        elif field_type.startswith("date"):
            field_cls = models.DateField(null=True)
        elif field_type.startswith("decimal"):
            field_cls = models.DecimalField(null=True, max_digits=1, decimal_places=6)
        else:
            raise DynamicModelError(f"Unknown field type. Got {field_type}.")
        return field_cls
