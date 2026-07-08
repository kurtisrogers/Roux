import csv
import io
import logging
from datetime import date, datetime, timedelta
from decimal import Decimal

from billing.models import Payment
from bookings.models import Attendance, Booking, Child, Session, SessionType
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from organisations.models import Site, TermDate

from operations.models import (
    Absence,
    AuthorisedCollector,
    ChildcareVoucher,
    RecurringBooking,
    SafeguardingCase,
    VoucherRedemption,
    WaitlistEntry,
)

logger = logging.getLogger(__name__)


def get_register_rows(session: Session) -> list[dict]:
    """Build register data for a session."""
    bookings = (
        session.bookings.select_related("child", "child__parent", "attendance")
        .prefetch_related("child__authorised_collectors")
        .order_by("child__last_name", "child__first_name")
    )
    rows = []
    for booking in bookings:
        child = booking.child
        attendance = getattr(booking, "attendance", None)
        rows.append(
            {
                "booking": booking,
                "child": child,
                "attendance": attendance,
                "allergies": child.allergies,
                "medical": child.medical_notes,
                "emergency": child.emergency_contact_phone,
                "collectors": list(child.authorised_collectors.filter(is_active=True)),
            }
        )
    return rows


def export_register_csv(session: Session) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "Child",
            "Age",
            "Status",
            "Payment",
            "Allergies",
            "Checked in",
            "Checked out",
            "Emergency contact",
        ]
    )
    for row in get_register_rows(session):
        b = row["booking"]
        att = row["attendance"]
        writer.writerow(
            [
                row["child"].full_name,
                row["child"].age,
                b.get_status_display(),
                b.get_payment_status_display(),
                row["allergies"] or "",
                att.checked_in_at.strftime("%H:%M") if att and att.checked_in_at else "",
                att.checked_out_at.strftime("%H:%M") if att and att.checked_out_at else "",
                row["emergency"],
            ]
        )
    return output.getvalue()


def close_register(session: Session, user, notes: str = "") -> Session:
    session.register_closed_at = timezone.now()
    session.register_closed_by = user
    if notes:
        session.register_notes = notes
    session.status = Session.Status.COMPLETED
    session.save(
        update_fields=["register_closed_at", "register_closed_by", "register_notes", "status"]
    )
    return session


def bulk_check_in(session: Session, user) -> int:
    count = 0
    for booking in session.bookings.filter(status=Booking.Status.CONFIRMED):
        attendance, _ = Attendance.objects.get_or_create(booking=booking)
        if not attendance.checked_in_at:
            attendance.checked_in_at = timezone.now()
            attendance.checked_in_by = user
            attendance.save()
            booking.status = Booking.Status.CHECKED_IN
            booking.save(update_fields=["status"])
            count += 1
    return count


def mark_no_show(booking: Booking) -> Booking:
    booking.status = Booking.Status.NO_SHOW
    booking.save(update_fields=["status"])
    return booking


def create_walk_in_booking(
    session: Session,
    child: Child,
    staff_user,
    *,
    payment_method: str = Payment.Method.CASH,
) -> Booking:
    method_map = {
        "cash": Payment.Method.CASH,
        "voucher": Payment.Method.VOUCHER,
        "waived": Payment.Method.WAIVED,
    }
    payment_method = method_map.get(payment_method, payment_method)
    booking, created = Booking.objects.get_or_create(
        child=child,
        session=session,
        defaults={
            "booked_by": child.parent,
            "status": Booking.Status.CONFIRMED,
            "payment_status": Booking.PaymentStatus.PAID
            if payment_method != Payment.Method.CARD
            else Booking.PaymentStatus.UNPAID,
            "source": Booking.Source.WALK_IN,
        },
    )
    if created and payment_method != Payment.Method.CARD:
        Payment.objects.create(
            organisation=session.organisation,
            booking=booking,
            amount=booking.price,
            status=Payment.Status.SUCCEEDED,
            payment_method=payment_method,
            description=f"Walk-in: {child.full_name}",
        )
    return booking


def add_to_waitlist(child: Child, session: Session) -> WaitlistEntry:
    max_pos = (
        WaitlistEntry.objects.filter(session=session)
        .order_by("-position")
        .values_list("position", flat=True)
        .first()
        or 0
    )
    entry, _ = WaitlistEntry.objects.get_or_create(
        child=child,
        session=session,
        defaults={"position": max_pos + 1},
    )
    return entry


def promote_waitlist(session: Session) -> Booking | None:
    if not session.is_full:
        entry = WaitlistEntry.objects.filter(session=session).order_by("position").first()
        if not entry:
            return None
        booking = Booking.objects.create(
            child=entry.child,
            session=session,
            booked_by=entry.child.parent,
            status=Booking.Status.CONFIRMED,
            source=Booking.Source.WAITLIST,
        )
        entry.delete()
        _reindex_waitlist(session)
        from notifications.services import notify_waitlist_promoted

        notify_waitlist_promoted(booking)
        return booking
    return None


def _reindex_waitlist(session: Session) -> None:
    for idx, entry in enumerate(
        WaitlistEntry.objects.filter(session=session).order_by("position"), start=1
    ):
        if entry.position != idx:
            entry.position = idx
            entry.save(update_fields=["position"])


def report_absence(
    child: Child, session: Session | None, absence_date: date, reason: str, user
) -> Absence:
    absence, _ = Absence.objects.get_or_create(
        child=child,
        date=absence_date,
        session=session,
        defaults={"reason": reason, "reported_by": user},
    )
    if session:
        Booking.objects.filter(child=child, session=session).update(status=Booking.Status.CANCELLED)
    from notifications.services import notify_absence_reported

    notify_absence_reported(absence)
    return absence


def generate_sessions_bulk(
    organisation,
    session_type: SessionType,
    site: Site,
    start_date: date,
    end_date: date,
    weekdays: list[int],
    start_time,
    end_time,
) -> int:
    created = 0
    current = start_date
    holidays = TermDate.objects.filter(
        organisation=organisation,
        is_holiday=True,
        start_date__lte=end_date,
        end_date__gte=start_date,
    )
    while current <= end_date:
        if current.weekday() in weekdays:
            in_holiday = any(h.start_date <= current <= h.end_date for h in holidays)
            if not in_holiday:
                _, was_created = Session.objects.get_or_create(
                    organisation=organisation,
                    site=site,
                    session_type=session_type,
                    date=current,
                    start_time=start_time,
                    defaults={"end_time": end_time, "status": Session.Status.SCHEDULED},
                )
                if was_created:
                    created += 1
        current += timedelta(days=1)
    return created


def apply_recurring_bookings(for_date: date | None = None) -> int:
    target = for_date or timezone.now().date()
    count = 0
    patterns = RecurringBooking.objects.filter(is_active=True).select_related(
        "child", "session_type", "site"
    )
    for pattern in patterns:
        if pattern.start_date > target:
            continue
        if pattern.end_date and pattern.end_date < target:
            continue
        if target.weekday() != pattern.weekday:
            continue
        if Absence.objects.filter(child=pattern.child, date=target).exists():
            continue
        session = Session.objects.filter(
            organisation=pattern.child.organisation,
            site=pattern.site,
            session_type=pattern.session_type,
            date=target,
            status=Session.Status.SCHEDULED,
        ).first()
        if not session or session.is_full:
            continue
        _, created = Booking.objects.get_or_create(
            child=pattern.child,
            session=session,
            defaults={
                "booked_by": pattern.child.parent,
                "status": Booking.Status.CONFIRMED,
                "source": Booking.Source.RECURRING,
            },
        )
        if created:
            count += 1
    return count


def calculate_late_fee(booking: Booking) -> Decimal:
    session = booking.session
    attendance = getattr(booking, "attendance", None)
    if not attendance or not attendance.checked_out_at:
        return Decimal("0")
    session_end = datetime.combine(session.date, session.end_time)
    if timezone.is_aware(attendance.checked_out_at):
        session_end = timezone.make_aware(session_end)
    grace = timedelta(minutes=session.session_type.late_pickup_grace_minutes)
    late = attendance.checked_out_at - session_end - grace
    if late.total_seconds() <= 0:
        return Decimal("0")
    blocks = int(late.total_seconds() // 900) + 1
    return session.session_type.late_pickup_fee * blocks


def apply_late_fee(booking: Booking) -> Decimal:
    fee = calculate_late_fee(booking)
    if fee > 0:
        booking.late_fee_amount = fee
        booking.save(update_fields=["late_fee_amount"])
    return fee


def redeem_voucher(booking: Booking, voucher: ChildcareVoucher) -> VoucherRedemption:
    amount = min(voucher.balance, booking.price)
    if amount <= 0:
        raise ValueError("Insufficient voucher balance")
    with transaction.atomic():
        voucher.balance -= amount
        voucher.save(update_fields=["balance"])
        redemption = VoucherRedemption.objects.create(
            voucher=voucher, booking=booking, amount=amount
        )
        booking.payment_status = Booking.PaymentStatus.PAID
        booking.save(update_fields=["payment_status"])
        Payment.objects.create(
            organisation=booking.session.organisation,
            booking=booking,
            amount=amount,
            status=Payment.Status.SUCCEEDED,
            payment_method=Payment.Method.VOUCHER,
            description=f"Voucher {voucher.reference}",
            metadata={"voucher_id": voucher.pk},
        )
    from notifications.services import notify_payment_received

    payment = booking.payments.latest("created_at")
    notify_payment_received(booking, payment)
    return redemption


def calculate_discounted_price(
    session_type: SessionType,
    child: Child,
    subsidy=None,
    sibling_count: int = 0,
    organisation=None,
) -> Decimal:
    price = session_type.price
    if subsidy:
        if subsidy.fixed_discount:
            price = max(Decimal("0"), price - subsidy.fixed_discount)
        elif subsidy.discount_percent:
            price = price * (1 - subsidy.discount_percent / 100)
    if child.pupil_premium:
        price = price * Decimal("0.85")
    if sibling_count > 1 and organisation:
        discount = organisation.sibling_discount_percent / 100
        price = price * (1 - discount)
    return price.quantize(Decimal("0.01"))


def create_safeguarding_case_from_incident(incident, user) -> SafeguardingCase:
    return SafeguardingCase.objects.create(
        organisation=incident.organisation,
        child=incident.child,
        incident=incident,
        title=f"Safeguarding: {incident.get_incident_type_display()}",
        status=SafeguardingCase.Status.OPEN,
        assigned_to=user,
    )


def get_organisation_analytics(organisation) -> dict:
    today = timezone.now().date()
    month_start = today.replace(day=1)
    revenue = Payment.objects.filter(
        organisation=organisation,
        status=Payment.Status.SUCCEEDED,
        created_at__date__gte=month_start,
    ).aggregate(total=Sum("amount"))["total"] or Decimal("0")
    return {
        "children_active": Child.objects.filter(organisation=organisation, is_active=True).count(),
        "sessions_this_month": Session.objects.filter(
            organisation=organisation, date__gte=month_start
        ).count(),
        "bookings_this_month": Booking.objects.filter(
            session__organisation=organisation,
            session__date__gte=month_start,
            status__in=[
                Booking.Status.CONFIRMED,
                Booking.Status.CHECKED_IN,
                Booking.Status.CHECKED_OUT,
            ],
        ).count(),
        "revenue_this_month": revenue,
        "voucher_payments": Payment.objects.filter(
            organisation=organisation,
            payment_method=Payment.Method.VOUCHER,
            created_at__date__gte=month_start,
        ).count(),
        "open_safeguarding": SafeguardingCase.objects.filter(
            organisation=organisation,
            status__in=[SafeguardingCase.Status.OPEN, SafeguardingCase.Status.INVESTIGATING],
        ).count(),
    }


def verify_collector_pin(collector: AuthorisedCollector, pin: str) -> bool:
    if not collector.pin_code:
        return True
    return collector.pin_code == pin


def checkout_with_collector(
    booking: Booking,
    user,
    collector: AuthorisedCollector | None,
    verified_name: str = "",
) -> Attendance:
    attendance, _ = Attendance.objects.get_or_create(booking=booking)
    attendance.checked_out_at = timezone.now()
    attendance.checked_out_by = user
    attendance.collected_by = collector
    attendance.collection_verified_name = verified_name or (collector.name if collector else "")
    attendance.save()
    booking.status = Booking.Status.CHECKED_OUT
    booking.save(update_fields=["status"])
    apply_late_fee(booking)
    return attendance
