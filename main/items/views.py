from typing import Any


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ItemsForm
from .models import Items

# Create your views here.


@login_required
def item_create_view(request):
    # Check if user has an active project (based on your project memory)
    if not hasattr(request, "active_project") or request.active_project is None:
        messages.error(request, "Please activate a project first.")
        return render(request, "projects/activate.html", {})

    form = ItemsForm(request.POST or None)
    if form.is_valid():
        item_obj = form.save(commit=False)
        item_obj.project = request.active_project
        item_obj.added_by = request.user
        item_obj.save()
        messages.success(request, f"Item '{item_obj.title}' created successfully!")
        return redirect("item_create")  # Redirect to clear form

    context = {
        "form": form,
        "active_project": request.active_project,
    }

    return render(request, "items/create.html", context)


@login_required
def item_list_view(request):
    # Check if user has an active project
    if not hasattr(request, "active_project") or request.active_project is None:
        messages.error(request, "Please activate a project first.")
        return render(request, "projects/activate.html", {})

    object_list = Items.objects.filter(project=request.active_project)  # type: ignore
    return render(request, "items/list.html", {"object_list": object_list})


@login_required
def item_detail_view(request, id=None):
    # Check if user has an active project
    if not hasattr(request, "active_project") or request.active_project is None:
        messages.error(request, "Please activate a project first.")
        return render(request, "projects/activate.html", {})

    instance: Items = get_object_or_404(Items, id=id, project=request.active_project)  # type: ignore
    return render(request, "items/detail.html", {"object": instance})


@login_required
def item_detail_update_view(request, id=None):
    if not hasattr(request, "active_project") or request.active_project is None:
        messages.error(request, "Please activate a project first.")
        return render(request, "projects/activate.html", {})

    data = request

    instance: Items = get_object_or_404(Items, id=id, project=request.active_project)  # type: ignore
    form = ItemsForm(data, instance=instance)
    form = ItemsForm(request.POST or None, instance=instance)
    if form.is_valid():
        item_obj = form.save(commit=False)
        item_obj.last_modified_by = request.user
        item_obj.save()
        messages.success(request, f"Item '{item_obj.title}' updated successfully!")
        return redirect("item_detail", id=item_obj.id)
    else:
        messages.error(request, "Error updating item.")


@login_required
def item_detail_delete_view(request, id=None):
    if not hasattr(request, "active_project") or request.active_project is None:
        messages.error(request, "Please activate a project first.")
        return render(request, "projects/activate.html", {})

    instance: Items = get_object_or_404(Items, id=id, project=request.active_project)
    instance.delete()
    messages.success(request, f"Item '{instance.title}' deleted successfully!")
    return redirect("item:list")
