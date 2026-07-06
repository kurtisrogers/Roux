from bookings.models import Attendance, Booking
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Booking)
def track_booking_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Booking.objects.get(pk=instance.pk)
            instance._previous_status = old.status
            instance._previous_payment_status = old.payment_status
        except Booking.DoesNotExist:
            instance._previous_status = None
            instance._previous_payment_status = None
    else:
        instance._previous_status = None
        instance._previous_payment_status = None


@receiver(post_save, sender=Booking)
def send_booking_notifications(sender, instance, created, **kwargs):
    from notifications.services import notify_booking_confirmed

    prev_status = getattr(instance, "_previous_status", None)
    if instance.status == Booking.Status.CONFIRMED and prev_status != Booking.Status.CONFIRMED:
        notify_booking_confirmed(instance)
    if instance.status == Booking.Status.CANCELLED and prev_status != Booking.Status.CANCELLED:
        from operations.services import promote_waitlist

        promote_waitlist(instance.session)


@receiver(pre_save, sender=Attendance)
def track_attendance_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old = Attendance.objects.get(pk=instance.pk)
            instance._had_check_in = bool(old.checked_in_at)
            instance._had_check_out = bool(old.checked_out_at)
        except Attendance.DoesNotExist:
            instance._had_check_in = False
            instance._had_check_out = False
    else:
        instance._had_check_in = False
        instance._had_check_out = False


@receiver(post_save, sender=Attendance)
def send_attendance_notifications(sender, instance, **kwargs):
    from notifications.services import notify_checked_in, notify_checked_out

    booking = instance.booking
    if instance.checked_in_at and not getattr(instance, "_had_check_in", False):
        notify_checked_in(booking)
    if instance.checked_out_at and not getattr(instance, "_had_check_out", False):
        notify_checked_out(booking)
