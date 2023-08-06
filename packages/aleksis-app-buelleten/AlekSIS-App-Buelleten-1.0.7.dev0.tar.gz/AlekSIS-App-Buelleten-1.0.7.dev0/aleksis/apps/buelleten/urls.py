from django.urls import path

from . import views

urlpatterns = [
    path("display_groups/", views.DisplayGroupListView.as_view(), name="display_groups"),
    path(
        "display_groups/create/",
        views.DisplayGroupCreateView.as_view(),
        name="create_display_group",
    ),
    path(
        "display_groups/<int:pk>/edit",
        views.DisplayGroupEditView.as_view(),
        name="edit_display_group",
    ),
    path(
        "display_groups/<int:pk>/", views.DisplayGroupFullView.as_view(), name="display_group_by_id"
    ),
    path(
        "api/impressive/<slug:slug>.txt",
        views.ImpressiveDisplayURLList.as_view(),
        name="impressive_display_list",
    ),
    path("displays/", views.DisplayListView.as_view(), name="displays"),
    path("displays/create/", views.DisplayCreateView.as_view(), name="create_display"),
    path("displays/<int:pk>/", views.DisplayEditView.as_view(), name="edit_display"),
    path(
        "slides/<int:pk>/edit/",
        views.SlideEditView.as_view(),
        name="edit_slide",
    ),
    path(
        "slides/<int:pk>/delete/",
        views.SlideDeleteView.as_view(),
        name="delete_slide",
    ),
    path(
        "slides/<str:app>/<str:model>/new/",
        views.SlideCreateView.as_view(),
        name="create_slide",
    ),
]
