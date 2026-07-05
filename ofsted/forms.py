from django import forms

from ofsted.models import Incident


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = (
            "session",
            "child",
            "incident_type",
            "severity",
            "occurred_at",
            "location",
            "description",
            "action_taken",
            "parent_notified",
            "ofsted_notifiable",
        )
        widgets = {
            "occurred_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "action_taken": forms.Textarea(attrs={"rows": 3}),
        }
