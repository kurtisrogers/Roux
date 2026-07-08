import logging

from django.conf import settings

logger = logging.getLogger(__name__)


def send_sms(recipient: str, message: str) -> bool:
    if not recipient:
        return False
    backend = getattr(settings, "SMS_BACKEND", "console")
    if backend == "console":
        logger.info("SMS to %s: %s", recipient, message)
        print(f"SMS to {recipient}: {message}")
        return True
    if backend == "twilio":
        return _send_twilio(recipient, message)
    return False


def _send_twilio(recipient: str, message: str) -> bool:
    try:
        from twilio.rest import Client

        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_FROM_NUMBER,
            to=recipient,
        )
        return True
    except Exception:
        logger.exception("Twilio SMS failed to %s", recipient)
        return False
