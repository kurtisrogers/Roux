from bookings.models import Booking, Child, SessionType
from django import forms
from organisations.models import Site

from operations.models import (
    Absence,
    AuthorisedCollector,
    ChildcareVoucher,
    MedicationAdministration,
    PaymentPlan,
    RecurringBooking,
    SafeguardingCase,
    StaffCompliance,
    StaffShift,
    SubsidyCode,
    Visitor,
)


class WalkInBookingForm(forms.Form):
    child = forms.ModelChoiceField(queryset=Child.objects.none())
    payment_method = forms.ChoiceField(
        choices=[
            ("cash", "Cash"),
            ("voucher", "Childcare voucher"),
            ("waived", "Waived"),
        ]
    )


class BulkSessionForm(forms.Form):
    session_type = forms.ModelChoiceField(queryset=SessionType.objects.none())
    site = forms.ModelChoiceField(queryset=Site.objects.none())
    start_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={"type": "date"}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={"type": "time"}))
    weekdays = forms.MultipleChoiceField(
        choices=RecurringBooking.Weekday.choices,
        widget=forms.CheckboxSelectMultiple,
    )


class RecurringBookingForm(forms.ModelForm):
    class Meta:
        model = RecurringBooking
        fields = ("child", "session_type", "site", "weekday", "start_date", "end_date")
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


class AuthorisedCollectorForm(forms.ModelForm):
    class Meta:
        model = AuthorisedCollector
        fields = ("name", "relationship", "phone", "pin_code", "is_primary", "is_active")


class CheckoutCollectorForm(forms.Form):
    collector = forms.ModelChoiceField(queryset=AuthorisedCollector.objects.none(), required=False)
    verified_name = forms.CharField(max_length=200, required=False)
    pin_code = forms.CharField(max_length=10, required=False)


class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ("child", "session", "date", "reason")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "reason": forms.Textarea(attrs={"rows": 2}),
        }


class StaffShiftForm(forms.ModelForm):
    class Meta:
        model = StaffShift
        fields = ("user", "site", "date", "start_time", "end_time", "notes")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class MedicationForm(forms.ModelForm):
    class Meta:
        model = MedicationAdministration
        fields = ("child", "session", "medication_name", "dose", "administered_at", "notes")
        widgets = {
            "administered_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class VisitorForm(forms.ModelForm):
    class Meta:
        model = Visitor
        fields = ("site", "name", "organisation_name", "purpose", "dbs_checked")
        widgets = {"purpose": forms.TextInput(attrs={"placeholder": "e.g. Contractor, volunteer"})}


class StaffComplianceForm(forms.ModelForm):
    class Meta:
        model = StaffCompliance
        fields = ("dbs_number", "dbs_expiry", "first_aid_expiry", "safeguarding_expiry", "notes")
        widgets = {
            "dbs_expiry": forms.DateInput(attrs={"type": "date"}),
            "first_aid_expiry": forms.DateInput(attrs={"type": "date"}),
            "safeguarding_expiry": forms.DateInput(attrs={"type": "date"}),
        }


class SafeguardingCaseForm(forms.ModelForm):
    class Meta:
        model = SafeguardingCase
        fields = ("title", "child", "status", "assigned_to", "notes")
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}


class SubsidyCodeForm(forms.ModelForm):
    class Meta:
        model = SubsidyCode
        fields = (
            "code",
            "name",
            "local_authority",
            "discount_percent",
            "fixed_discount",
            "is_active",
        )


class ChildcareVoucherForm(forms.ModelForm):
    class Meta:
        model = ChildcareVoucher
        fields = ("parent", "child", "provider", "reference", "balance", "is_active")


class VoucherRedeemForm(forms.Form):
    voucher = forms.ModelChoiceField(queryset=ChildcareVoucher.objects.none())
    booking = forms.ModelChoiceField(queryset=Booking.objects.none())


class PaymentPlanForm(forms.ModelForm):
    class Meta:
        model = PaymentPlan
        fields = (
            "child",
            "name",
            "term_start",
            "term_end",
            "total_amount",
            "installments",
            "status",
        )
        widgets = {
            "term_start": forms.DateInput(attrs={"type": "date"}),
            "term_end": forms.DateInput(attrs={"type": "date"}),
        }


class RefundForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    reason = forms.CharField(max_length=255, required=False)
