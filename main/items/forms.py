from .models import Items
from django import forms


class ItemsForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "block w-full px-4 py-3 text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors",
                    "placeholder": "Enter item title...",
                    "maxlength": "120",
                    "required": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "block w-full px-4 py-3 text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors resize-none",
                    "placeholder": "Enter item description... (optional)",
                    "rows": 6,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom validation and help text
        self.fields["title"].help_text = "Maximum 120 characters"
        self.fields["description"].help_text = (
            "Provide additional details about this item"
        )

        # Make title required
        self.fields["title"].required = True

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if title:
            title = title.strip()
            if len(title) < 3:
                raise forms.ValidationError("Title must be at least 3 characters long.")
        return title
