from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # CRUD operations
    path("", views.project_list_view, name="project_list"),
    path("create/", views.project_create_view, name="project_create"),
    path("<slug:handle>/", views.project_detail_view, name="project_detail"),
    path("<slug:handle>/update/", views.project_update_view, name="project_update"),
    path("<slug:handle>/delete/", views.project_delete_view, name="project_delete"),
    path(
        "activate/<str:handle>/", views.activate_prject_views, name="project_activate"
    ),
    path(
        "deactivate/<str:handle>/",
        views.deactivate_prject_views,
        name="project_deactivate",
    ),
]
