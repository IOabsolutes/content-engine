import time
import logging
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import Project, AnonymousProject
from django.core.cache import cache


logger = logging.getLogger(__name__)


class ProjectMiddleware:
    """
    Middleware to handle project activation context for the Content Engine.
    Ensures that project-specific functionality works with session data.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if not hasattr(request, "project"):
            request.project = AnonymousProject()
            if request.user.is_authenticated:
                project_handle = request.session.get("project_handle")
                request.project = Project.objects.get("project_handle")  # type: ignore
                project_obj = None
                cache_str = None
                if project_handle is not None:
                    cache_str = f"project_{project_handle}"
                    project_obj = cache.get(cache_str)
                    if project_obj is None and project_handle is not None:
                        try:
                            project_obj = Project.objects.get(handle=project_handle)  # type: ignore
                        except:
                            project_obj = None

                if project_obj is not None:
                    cache.set(cache_str, project_obj)
                    request.project = project_obj
        return self.get_response(request)

    def process_request(self, request):
        """Add project context to request if user is authenticated and has active project."""
        request.active_project = None

        if request.user.is_authenticated:
            project_handle = request.session.get("project_handle")
            if project_handle:
                try:
                    project = Project.objects.get(  # type: ignore
                        owner=request.user, handle=project_handle, active=True
                    )  # type: ignore
                    request.active_project = project
                except Project.DoesNotExist:  # type: ignore  # type: ignore
                    # Clean up invalid session data
                    del request.session["project_handle"]
                    logger.warning(
                        f"Invalid project handle removed from session: {project_handle}"
                    )

    def process_response(self, request, response):
        """Add project information to response headers for debugging."""
        if hasattr(request, "active_project") and request.active_project:
            response["X-Active-Project"] = request.active_project.handle
        return response
