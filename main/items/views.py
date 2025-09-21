from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ItemsForm
from .models import Items

# Create your views here.


@login_required
def item_create_view(request):
    # Check if user has an active project (based on your project memory)
    if not hasattr(request, 'active_project') or request.active_project is None:
        messages.error(request, "Please activate a project first.")
        return render(request, "projects/activate.html", {})
    
    form = ItemsForm(request.POST or None)
    if form.is_valid():
        item_obj = form.save(commit=False)
        item_obj.project = request.active_project
        item_obj.added_by = request.user
        item_obj.save()
        messages.success(request, f"Item '{item_obj.title}' created successfully!")
        return redirect('item_create')  # Redirect to clear form
    
    context = {
        "form": form,
        "active_project": request.active_project,
    }

    return render(request, "items/create.html", context)
