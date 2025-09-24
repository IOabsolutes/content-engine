from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project, AnonymousProject
from .forms import ProjectForm


def delete_project_from_session(request):
    try:
        del request.session["project_handle"]
    except:
        pass
    try:
        request.project = AnonymousProject()
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


# CRUD Views
@login_required
def project_list_view(request):
    """List all projects owned by the current user"""
    projects = Project.objects.filter(owner=request.user).order_by('-updated')  # type: ignore
    context = {
        'object_list': projects,
        'active_project': getattr(request, 'active_project', None)
    }
    return render(request, 'projects/list.html', context)


@login_required
def project_detail_view(request, id=None):
    """Show details of a specific project"""
    project = get_object_or_404(Project, id=id, owner=request.user)
    context = {
        'object': project,
        'active_project': getattr(request, 'active_project', None)
    }
    return render(request, 'projects/detail.html', context)


@login_required
def project_create_view(request):
    """Create a new project"""
    form = ProjectForm(request.POST or None)
    if form.is_valid():
        project = form.save(commit=False)
        project.owner = request.user
        project.save()
        messages.success(request, f"Project '{project.title}' created successfully!")
        return redirect('projects:project_detail', id=project.id)
    
    context = {
        'form': form,
        'active_project': getattr(request, 'active_project', None)
    }
    return render(request, 'projects/create.html', context)


@login_required
def project_update_view(request, id=None):
    """Update an existing project"""
    project = get_object_or_404(Project, id=id, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    
    if form.is_valid():
        updated_project = form.save()
        messages.success(request, f"Project '{updated_project.title}' updated successfully!")
        return redirect('projects:project_detail', id=updated_project.id)
    
    context = {
        'form': form,
        'object': project,
        'active_project': getattr(request, 'active_project', None)
    }
    return render(request, 'projects/update.html', context)


@login_required
def project_delete_view(request, id=None):
    """Delete an existing project"""
    project = get_object_or_404(Project, id=id, owner=request.user)
    
    if request.method == 'POST':
        # Check confirmation
        confirm_title = request.POST.get('confirm_title', '').strip()
        confirm_understand = request.POST.get('confirm_understand')
        
        if confirm_title == project.title and confirm_understand:
            project_title = project.title
            # If this is the active project, deactivate it first
            if hasattr(request, 'active_project') and request.active_project and request.active_project.id == project.id:
                delete_project_from_session(request)
            project.delete()
            messages.success(request, f"Project '{project_title}' deleted successfully!")
            return redirect('projects:project_list')
        else:
            messages.error(request, "Confirmation failed. Please verify the project title and checkbox.")
    
    context = {
        'object': project,
        'active_project': getattr(request, 'active_project', None)
    }
    return render(request, 'projects/delete.html', context)
