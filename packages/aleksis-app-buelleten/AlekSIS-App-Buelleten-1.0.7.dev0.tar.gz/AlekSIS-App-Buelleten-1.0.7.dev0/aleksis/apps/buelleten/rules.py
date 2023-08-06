import rules

from aleksis.core.util.predicates import (
    has_any_object,
    has_global_perm,
    has_object_perm,
    has_person,
)

from .models.base import Display, DisplayGroup, Slide
from .models.slides import ForeignURLSlide, StaticContentSlide, UploadedFileSlide

# Displays

view_displays_predicate = has_person & (
    has_global_perm("buelleten.view_display") | has_any_object("paweljong.view_display", Display)
)
rules.add_perm("buelleten.view_displays_rule", view_displays_predicate)

# View display
view_display_predicate = has_person & (
    has_global_perm("buelleten.view_display") | has_object_perm("paweljong.view_display")
)
rules.add_perm("buelleten.view_display_rule", view_display_predicate)

# Edit display
change_display_predicate = has_person & (
    has_global_perm("buelleten.change_display") | has_object_perm("paweljong.change_display")
)
rules.add_perm("buelleten.change_display_rule", change_display_predicate)

# Delete display
delete_display_predicate = has_person & (
    has_global_perm("buelleten.delete_display") | has_object_perm("paweljong.delete_display")
)
rules.add_perm("buelleten.delete_display_rule", delete_display_predicate)

# Create displays
create_displays_predicate = has_person & (
    has_global_perm("buelleten.create_display")
    | has_any_object("buelleten.create_display", Display)
)
rules.add_perm("buelleten.create_displays_rule", create_displays_predicate)

# Display groups

view_display_groups_predicate = has_person & (
    has_global_perm("buelleten.view_display_group")
    | has_any_object("buelleten.view_display_group", DisplayGroup)
)
rules.add_perm("buelleten.view_display_groups_rule", view_display_groups_predicate)

# View display_group
view_display_group_predicate = has_person & (
    has_global_perm("buelleten.view_display_group")
    | has_object_perm("buelleten.view_display_group")
)
rules.add_perm("buelleten.view_display_group_rule", view_display_group_predicate)

# Edit display_group
change_display_group_predicate = has_person & (
    has_global_perm("buelleten.change_display_group")
    | has_object_perm("buelleten.change_display_group")
)
rules.add_perm("buelleten.change_display_group_rule", change_display_group_predicate)

# Delete display_group
delete_display_group_predicate = has_person & (
    has_global_perm("buelleten.delete_display_group")
    | has_object_perm("buelleten.delete_display_group")
)
rules.add_perm("buelleten.delete_display_group_rule", delete_display_group_predicate)

# Create display_groups
create_display_groups_predicate = has_person & (
    has_global_perm("buelleten.create_display_group")
    | has_any_object("buelleten.create_display_group", DisplayGroup)
)
rules.add_perm("buelleten.create_display_groups_rule", create_display_groups_predicate)
