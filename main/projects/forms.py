from django import forms
from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "active"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors",
                    "placeholder": "Enter project title...",
                    "maxlength": "120",
                    "required": True,
                }
            ),
            "active": forms.CheckboxInput(
                attrs={
                    "class": "h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom validation and help text
        self.fields["title"].help_text = "Maximum 120 characters"
        self.fields["active"].help_text = (
            "Active projects can be selected for content management"
        )

        # Make title required
        self.fields["title"].required = True

        # Add custom labels
        self.fields["title"].label = "Project Title"
        self.fields["active"].label = "Active Status"

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title:
            title = title.strip()
            if len(title) < 3:
                raise forms.ValidationError("Title must be at least 3 characters long.")
            # Check for duplicate titles for the same owner (will be handled in view)
        return title