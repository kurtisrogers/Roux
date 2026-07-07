from django import forms

from programme.models import Activity, Programme, ScheduleEvent, WeekPack, WeekPackBlock


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = (
            "name",
            "description",
            "category",
            "default_duration_minutes",
            "resources",
            "is_active",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "resources": forms.Textarea(attrs={"rows": 2}),
        }


class WeekPackForm(forms.ModelForm):
    class Meta:
        model = WeekPack
        fields = ("name", "description", "is_active")
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


class WeekPackBlockForm(forms.ModelForm):
    class Meta:
        model = WeekPackBlock
        fields = (
            "weekday",
            "start_time",
            "end_time",
            "activity",
            "label",
            "notes",
            "sort_order",
            "is_running_period",
        )
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = (
            "name",
            "site",
            "session_type",
            "start_date",
            "end_date",
            "week_a_pack",
            "week_b_pack",
            "anchor_date",
            "first_week",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "anchor_date": forms.DateInput(attrs={"type": "date"}),
        }


class ScheduleEventSingleForm(forms.ModelForm):
    class Meta:
        model = ScheduleEvent
        fields = (
            "date",
            "start_time",
            "end_time",
            "activity",
            "label",
            "notes",
            "replaces_day",
            "sort_order",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class ScheduleEventClosureForm(forms.ModelForm):
    class Meta:
        model = ScheduleEvent
        fields = (
            "programme",
            "site",
            "session_type",
            "start_date",
            "end_date",
            "label",
            "notes",
        )
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class DayOverrideForm(forms.Form):
    ACTION_CHOICES = [
        ("default", "Use default week (remove overrides)"),
        ("replace", "Replace whole day"),
        ("add", "Add / merge extra slots"),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES)
    start_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}))
    end_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={"type": "time"}))
    activity = forms.ModelChoiceField(queryset=Activity.objects.none(), required=False)
    label = forms.CharField(max_length=200, required=False)
    notes = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 2}))
    replaces_day = forms.BooleanField(required=False, initial=True)
