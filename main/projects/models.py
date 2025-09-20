from django.conf import settings
from django.db import models
from django.utils.text import slugify
from main.utils.generators import unique_slug_generator

User = settings.AUTH_USER_MODEL


class AnonymousProject(models.Model):
    value = None


class Project(models.Model):
    owner = models.ForeignKey(User, on_delete=models.SET_NULL)
    title = models.CharField(max_length=120)
    handle = models.SlugField(unique=True, blank=True, null=True)
    active = models.BooleanField(default=True)  # type: ignore
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def save(self, *args, **kwargs):
        if not self.handle:
            self.handle = unique_slug_generator(self, slug_field="handle")
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-updated", "-timestamp"]

    def __str__(self):
        return f"{self.title} ({self.handle})"
