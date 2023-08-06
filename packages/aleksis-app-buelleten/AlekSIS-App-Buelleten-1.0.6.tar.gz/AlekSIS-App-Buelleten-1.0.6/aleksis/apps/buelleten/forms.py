from django import forms
from django.utils.translation import gettext_lazy as _

from material import Fieldset, Layout, Row

from aleksis.core.mixins import ExtensibleForm

from .models.base import Display, DisplayGroup, Slide
from .models.slides import ForeignURLSlide, StaticContentSlide, UploadedFileSlide


class EditDisplayGroupForm(ExtensibleForm):

    layout = Layout("name", "slug")

    class Meta:
        model = DisplayGroup
        exclude = []


class EditDisplayForm(ExtensibleForm):

    layout = Layout(
        "display_group",
        Row("hostname", "profile"),
    )

    class Meta:
        model = Display
        exclude = []
