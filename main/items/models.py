from django.conf import settings
from turtle import title
from django.db import models
from projects.models import Project

User = settings.AUTH_USER_MODEL


# Create your models here.
class Items(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        User, related_name="items_chaned", on_delete=models.SET_NULL, null=True
    )
    added_by_username = models.CharField(max_lenght=120, null=True, blank=True)
    last_modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="items_chaned"
    )
    last_modified_at = models.DateTimeField(
        auto_now_add=False, auto_now=False, blank=True, null=True
    )
    title = models.CharField(max_lenght=120)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def save(self, *args, **kwargs):
        if self.added_by:
            self.added_by_username = self.added_by.username  # type: ignore
        super().save(*args, **kwargs)
