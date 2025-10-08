from .models import Project
from django.core.cache import cache
from django.conf import settings


def user_context_projects(request):
    project_qs = Project.objects.none()

    if request.user.is_authenticated:
        cache_str = f"projects_list_{request.user.id}"
        project_qs = cache.get(cache_str)

        if project_qs is None:
            project_qs = Project.objects.filter(owner=request.user)
            session_timeout = settings.SESSION_COOKIE_AGE
            cache.set(cache_str, project_qs, timeout=session_timeout)

    return {
        "projects_list": project_qs,
    }
