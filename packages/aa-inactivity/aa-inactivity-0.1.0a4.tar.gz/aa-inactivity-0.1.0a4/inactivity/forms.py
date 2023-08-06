from django import forms

from .models import LeaveOfAbsence


class CreateRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveOfAbsence
        fields = ["start", "end", "notes"]
