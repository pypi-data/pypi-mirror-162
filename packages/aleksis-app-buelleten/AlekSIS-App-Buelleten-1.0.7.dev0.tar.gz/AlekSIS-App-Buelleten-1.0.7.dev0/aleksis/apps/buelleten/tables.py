from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import A


class DisplayGroupsTable(tables.Table):
    class Meta:
        attrs = {"class": "highlight"}

    name = tables.LinkColumn("display_group_by_id", args=[A("id")])
    slug = tables.Column()
    edit = tables.LinkColumn(
        "edit_display_group",
        args=[A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
        verbose_name=_("Actions"),
    )


class DisplaysTable(tables.Table):
    class Meta:
        attrs = {"class": "highlight"}

    hostname = tables.LinkColumn("edit_display", args=[A("id")])
    profile = tables.Column()
    edit = tables.LinkColumn(
        "edit_display",
        args=[A("id")],
        text=_("Edit"),
        attrs={"a": {"class": "btn-flat waves-effect waves-orange orange-text"}},
        verbose_name=_("Actions"),
    )


class SlidesTable(tables.Table):
    class Meta:
        attrs = {"class": "highlight"}

    slide_name = tables.LinkColumn("edit_slide", args=[A("id")], accessor="pk")
    delete = tables.LinkColumn(
        "delete_slide",
        args=[A("id")],
        text=_("Delete"),
        attrs={"a": {"class": "btn-flat waves-effect waves-red red-text"}},
        verbose_name=_("Actions"),
    )

    def render_slide_name(self, value, record):
        return record._meta.verbose_name
