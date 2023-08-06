from typing import Any, Type

from django.contrib.contenttypes.models import ContentType
from django.forms.models import BaseModelForm, modelform_factory
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.generic import View
from django.views.generic.detail import DetailView, SingleObjectMixin

from django_tables2 import RequestConfig, SingleTableView
from oauth2_provider.views.mixins import ScopedResourceMixin
from rules.contrib.views import PermissionRequiredMixin

from aleksis.core.mixins import (
    AdvancedCreateView,
    AdvancedDeleteView,
    AdvancedEditView,
    SuccessNextMixin,
)
from aleksis.core.util.auth_helpers import ClientProtectedResourceMixin

from .filters import DisplaysFilter
from .forms import EditDisplayForm, EditDisplayGroupForm
from .models.base import Display, DisplayGroup, Slide
from .models.slides import ForeignURLSlide, StaticContentSlide, UploadedFileSlide
from .tables import DisplayGroupsTable, DisplaysTable, SlidesTable


class DisplayListView(PermissionRequiredMixin, SingleTableView):
    """Table of all displays."""

    model = Display
    table_class = DisplaysTable
    permission_required = "buelleten.view_displays_rule"
    template_name = "buelleten/display/list.html"


@method_decorator(never_cache, name="dispatch")
class DisplayCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for displays."""

    model = Display
    form_class = EditDisplayForm
    permission_required = "buelleten.create_display_rule"
    template_name = "buelleten/display/create.html"
    success_url = reverse_lazy("displays")
    success_message = _("The display has been created.")


@method_decorator(never_cache, name="dispatch")
class DisplayEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for displays."""

    model = Display
    form_class = EditDisplayForm
    permission_required = "buelleten.change_display_rule"
    template_name = "buelleten/display/edit.html"
    success_url = reverse_lazy("displays")
    success_message = _("The display has been saved.")


class DisplayDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete view for displays."""

    model = Display
    permission_required = "buelleten.delete_display_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("displays")
    success_message = _("The display has been deleted.")


class DisplayGroupFullView(PermissionRequiredMixin, DetailView):

    model = DisplayGroup
    template_name = "buelleten/display_group/full.html"
    permission_required = "buelleten.view_display_group_rule"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        displays = Display.objects.filter(display_group=self.get_object())
        displays_filter = DisplaysFilter(self.request.GET, queryset=displays)
        context["displays_filter"] = displays_filter

        displays_table = DisplaysTable(displays_filter.qs)
        RequestConfig(self.request).configure(displays_table)
        context["displays_table"] = displays_table

        slides = Slide.objects.filter(display_group=self.get_object())
        slides_table = SlidesTable(slides)
        RequestConfig(self.request).configure(slides_table)
        context["slides_table"] = slides_table

        context["slide_types"] = [
            (ContentType.objects.get_for_model(m, False), m) for m in Slide.__subclasses__()
        ]

        return context


class DisplayGroupListView(PermissionRequiredMixin, SingleTableView):
    """Table of all display groups."""

    model = DisplayGroup
    table_class = DisplayGroupsTable
    permission_required = "buelleten.view_display_groups_rule"
    template_name = "buelleten/display_group/list.html"


@method_decorator(never_cache, name="dispatch")
class DisplayGroupCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for display groups."""

    model = DisplayGroup
    form_class = EditDisplayGroupForm
    permission_required = "buelleten.create_display group_rule"
    template_name = "buelleten/display_group/create.html"
    success_url = reverse_lazy("display_groups")
    success_message = _("The display group has been created.")


@method_decorator(never_cache, name="dispatch")
class DisplayGroupEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for display groups."""

    model = DisplayGroup
    form_class = EditDisplayGroupForm
    permission_required = "buelleten.change_display group_rule"
    template_name = "buelleten/display_group/edit.html"
    success_url = reverse_lazy("display_groups")
    success_message = _("The display group has been saved.")


class DisplayGroupDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete view for display groups."""

    model = DisplayGroup
    permission_required = "buelleten.delete_display group_rule"
    template_name = "core/pages/delete.html"
    success_url = reverse_lazy("display_groups")
    success_message = _("The display group has been deleted.")


@method_decorator(never_cache, name="dispatch")
class SlideEditView(PermissionRequiredMixin, AdvancedEditView):
    """Edit view for slides."""

    def get_form_class(self) -> Type[BaseModelForm]:
        return modelform_factory(self.object.__class__, fields=self.fields)

    model = Slide
    fields = "__all__"
    permission_required = "buelleten.edit_slide_rule"
    template_name = "buelleten/slide/edit.html"
    success_message = _("The slide has been saved.")

    def get_success_url(self):
        return reverse("display_group_by_id", kwargs={"pk": self.object.id})


@method_decorator(never_cache, name="dispatch")
class SlideCreateView(PermissionRequiredMixin, AdvancedCreateView):
    """Create view for slides."""

    def get_model(self, request, *args, **kwargs):
        app_label = kwargs.get("app")
        model = kwargs.get("model")
        ct = get_object_or_404(ContentType, app_label=app_label, model=model)
        return ct.model_class()

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["model"] = self.model
        return context

    def get(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.model = self.get_model(request, *args, **kwargs)
        return super().post(request, *args, **kwargs)

    fields = "__all__"
    permission_required = "buelleten.add_slide_rule"
    template_name = "buelleten/slide/create.html"
    success_message = _("The slide has been created.")

    def get_success_url(self):
        return reverse("display_group_by_id", kwargs={"pk": self.object.display_group.id})


class SlideDeleteView(PermissionRequiredMixin, AdvancedDeleteView):
    """Delete view for slides."""

    model = Slide
    permission_required = "buelleten.delete_slide_rule"
    template_name = "core/pages/delete.html"
    success_message = _("The slide has been deleted.")

    def get_success_url(self):
        return reverse("display_group_by_id", kwargs={"pk": self.object.display_group.id})


class DisplayGroupAPIBaseView(
    ScopedResourceMixin, ClientProtectedResourceMixin, SingleObjectMixin, View
):
    """Base view for all views related to display groups accessing data."""

    model = DisplayGroup

    def _get_display_group(self):
        object = self.get_object()
        if isinstance(object, DisplayGroup):
            return object
        elif isinstance(object, Display):
            return object.display_group
        elif isinstance(object, Slide):
            return object.display_group
        else:
            return TypeError("Unsupported object type")

    def get_scopes(self, *args, **kwargs) -> list[str]:
        """Return the scope needed to access the list."""
        display_group = self._get_display_group()
        return [self.get_object().scope]


class ImpressiveDisplayURLList(DisplayGroupAPIBaseView):
    """Retrieve the URL list for an impressive-display display."""

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        display_group = self._get_display_group()

        slide_urls = []
        for slide in display_group.slides.all():
            if "impressive" in slide._supported_profiles:
                slide_urls.append(slide.get_public_url(request=request))
            else:
                slide_urls.append(f"# Slide {slide} not supported on this display profile")

        return HttpResponse("\n".join(slide_urls) + "\n", content_type="text/plain")
