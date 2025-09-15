from django import forms
from .models import Capsule
from django.utils import timezone

class CapsuleForm(forms.ModelForm):
    release_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text="Use your local time. Format: YYYY-MM-DD HH:MM"
    )

    class Meta:
        model = Capsule
        fields = ["title", "message", "file", "release_date", "is_public"]

    def clean_release_date(self):
        dt = self.cleaned_data["release_date"]
        # If widget returns naive local datetime, convert to aware in view or accept as is.
        if dt <= timezone.now():
            raise forms.ValidationError("Release date must be in the future.")
        return dt
