from django.utils.translation import gettext_lazy as _

MENUS = {
    "NAV_MENU_CORE": [
        {
            "name": _("Digital signage"),
            "root": True,
            "url": "#",
            "validators": [
                "menu_generator.validators.is_authenticated",
                "aleksis.core.util.core_helpers.has_person",
            ],
            "submenu": [
                {
                    "name": _("Display groups"),
                    "url": "display_groups",
                    "validators": [
                        (
                            "aleksis.core.util.predicates.permission_validator",
                            "buelleten.view_display_groups_rule",
                        ),
                    ],
                },
            ],
        }
    ]
}
