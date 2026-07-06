from bookings.models import Booking, Child, Session, SessionType
from cms.models import ContactSubmission, NavigationItem, Page, PageBlock, SiteSettings
from django import forms
from organisations.models import Organisation, Site, TermDate


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = (
            "first_name",
            "last_name",
            "date_of_birth",
            "school_year",
            "allergies",
            "medical_notes",
            "dietary_requirements",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "photo_consent",
            "pupil_premium",
            "fsm_eligible",
        )
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "medical_notes": forms.Textarea(attrs={"rows": 2}),
            "dietary_requirements": forms.Textarea(attrs={"rows": 2}),
        }


class SessionTypeForm(forms.ModelForm):
    class Meta:
        model = SessionType
        fields = (
            "name",
            "category",
            "description",
            "price",
            "capacity",
            "age_min",
            "age_max",
            "duration_minutes",
            "late_pickup_fee",
            "late_pickup_grace_minutes",
            "is_active",
        )


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = (
            "site",
            "session_type",
            "date",
            "start_time",
            "end_time",
            "status",
            "staff",
            "notes",
        )
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
            "staff": forms.CheckboxSelectMultiple(),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ("child", "session", "special_requirements", "status", "payment_status")
        widgets = {
            "special_requirements": forms.Textarea(attrs={"rows": 2}),
        }


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = (
            "name",
            "slug",
            "email",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "county",
            "postcode",
            "ofsted_number",
            "is_active",
        )


class SiteForm(forms.ModelForm):
    class Meta:
        model = Site
        fields = (
            "name",
            "slug",
            "address_line1",
            "address_line2",
            "city",
            "postcode",
            "phone",
            "capacity",
            "is_active",
        )


class TermDateForm(forms.ModelForm):
    class Meta:
        model = TermDate
        fields = ("name", "start_date", "end_date", "is_holiday")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = (
            "site_name",
            "tagline",
            "logo",
            "primary_colour",
            "contact_email",
            "contact_phone",
            "address",
            "facebook_url",
            "instagram_url",
            "twitter_url",
            "footer_text",
            "google_analytics_id",
        )


class PageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = (
            "title",
            "slug",
            "meta_description",
            "is_homepage",
            "is_published",
            "show_in_nav",
        )


class PageBlockForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 12, "class": "block-content-json"}),
        help_text="JSON content for this block.",
    )

    class Meta:
        model = PageBlock
        fields = ("block_type", "is_visible")


class NavigationItemForm(forms.ModelForm):
    class Meta:
        model = NavigationItem
        fields = ("label", "page", "external_url", "order", "is_visible")


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ("name", "email", "phone", "message")
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
