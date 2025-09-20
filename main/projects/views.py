from django.contrib import messages
from django.shortcuts import redirect, render
from .models import Project


def delete_project_from_session(request):
    try:
        del request.session["project_handle"]
    except:
        pass


# Create your views here.
def activate_prject_views(request, handle=None):
    try:
        project_obj = Project.objects.get(owner=request.user, handle=handle)  # type: ignore
    except Project.DoesNotExist:  # type: ignore
        project_obj = None

    if project_obj is None:
        delete_project_from_session(request=request)
        messages.error(request, "Project could not activate, try again")
        return redirect("/")

    request.session["project_handle"] = handle
    messages.success(request, "Project activated successfully")
    return redirect("/")


def deactivate_prject_views(request, handle=None):
    delete_project_from_session(request=request)
    messages.success(request, "Project deactivated successfully")
    return redirect("/")
