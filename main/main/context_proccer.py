from django.core.cache import cache
from django.urls import reverse


def site_urls(request):
    project_create_url = reverse("projects:create")
    return {
        "home_url": reverse("home"),
        "aobut_url": reverse("about"),
        "project_create_url": project_create_url,
    }
