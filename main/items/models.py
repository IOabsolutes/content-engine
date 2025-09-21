from django.conf import settings
from django.db import models
from django.utils import timezone
from projects.models import Project

User = settings.AUTH_USER_MODEL


# Create your models here.
class Items(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    added_by = models.ForeignKey(
        User, related_name="items_added", on_delete=models.SET_NULL, null=True
    )
    added_by_username = models.CharField(max_length=120, null=True, blank=True)
    last_modified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="items_modified"
    )
    last_modified_at = models.DateTimeField(auto_now=True)
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Update modified timestamp
        self.last_modified_at = timezone.now()
        
        # Set username if user is provided
        if self.added_by:
            self.added_by_username = self.added_by.username  # type: ignore
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} ({self.project.title})"  # type: ignore
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
    
    @property
    def short_description(self):
        """Return truncated description for list views"""
        if self.description:
            desc_str = str(self.description)  # Convert to string
            return desc_str[:100] + '...' if len(desc_str) > 100 else desc_str
        return 'No description provided'
