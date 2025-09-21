from django.contrib import admin
from .models import Items


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ["title", "project", "added_by", "timestamp", "last_modified_at"]
    list_filter = ["project", "timestamp", "last_modified_at"]
    search_fields = ["title", "description", "project__title"]
    readonly_fields = ["added_by_username", "timestamp", "last_modified_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("title", "description", "project")}),
        (
            "Tracking Information",
            {
                "fields": (
                    "added_by",
                    "added_by_username",
                    "last_modified_by",
                    "timestamp",
                    "last_modified_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.added_by = request.user
        obj.last_modified_by = request.user
        super().save_model(request, obj, form, change)
