from django.apps import apps
from django.db import models
from django.db.models import functions
from django.utils.translation import gettext_lazy as _

from aleksis.core.util.apps import AppConfig


class DefaultConfig(AppConfig):
    name = "aleksis.apps.buelleten"
    verbose_name = "AlekSIS — Bülleten"
    dist_name = "AlekSIS-App-Buelleten"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/onboarding//AlekSIS-App-Buelleten",
    }
    licence = "EUPL-1.2+"
    copyright_info = (
        ([2021], "Tom Teichler", "dev@jonathanweth.de"),
        ([2022], "Dominik George", "dominik.george@teckids.org"),
        ([2022], "Tom Teichler", "tom.teichler@teckids.org"),
    )

    @classmethod
    def get_all_scopes(cls) -> dict[str, str]:
        """Return all OAuth scopes and their descriptions for this app."""
        DisplayGroup = apps.get_model("buelleten", "DisplayGroup")
        label_prefix = _("Access content for display group")
        scopes = dict(
            DisplayGroup.objects.annotate(
                scope=functions.Concat(
                    models.Value(f"{DisplayGroup.SCOPE_PREFIX}_"),
                    models.F("slug"),
                    output_field=models.CharField(),
                ),
                label=functions.Concat(models.Value(f"{label_prefix}: "), models.F("name")),
            )
            .values_list("scope", "label")
            .distinct()
        )
        return scopes
