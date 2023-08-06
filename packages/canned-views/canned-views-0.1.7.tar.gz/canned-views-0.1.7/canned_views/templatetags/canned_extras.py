from django import template
from django.urls import reverse
from django.utils.html import format_html
from edc_constants.constants import YES
from edc_dashboard import url_names

register = template.Library()


@register.simple_tag(takes_context=False)
def object_list_to_table(object_list, report_definition):
    table = ['<table id="table_id" class="display">\n']
    columns = None
    for obj in object_list:
        if not columns:
            columns = [k for k in obj.__dict__ if not k.startswith("_") and k != "id"]
            row = ["<thead>\n  <tr>\n"]
            for col in columns:
                row.append(f"    <th>{col}</th>\n")
            row.append("  </tr>\n</thead>\n<tbody>\n")
            table.append("".join(row))
        row = ["  <tr>\n"]
        for col in columns:
            if (
                report_definition.reverse_url == YES
                and col == report_definition.linked_column_name
            ):
                value = rendered_url(obj, **report_definition.__dict__)
            else:
                value = getattr(obj, col)
            row.append(f"    <td>{value}</td>\n")
        row.append("  </tr>\n")
        table.append("".join(row))
    table.append("</tbody>\n</table>")
    return format_html("".join(table))


def rendered_url(
    obj,
    linked_column_name=None,
    reverse_url_name=None,
    reverse_url_args=None,
    **kwargs,  # noqa
):
    linked_column_value = getattr(obj, linked_column_name)
    kwargs = {}
    url_name = url_names.get(reverse_url_name)
    for col in reverse_url_args.replace(" ", "").split(","):
        kwargs.update({col: getattr(obj, col)})
    return format_html(
        f'<A href="{reverse(url_name, kwargs=kwargs)}">' f"{linked_column_value}</A>"
    )
