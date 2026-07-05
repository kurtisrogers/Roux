import base64
import logging
import secrets
from datetime import timedelta
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.utils import timezone

from finance.models import XeroConnection, XeroInvoice

logger = logging.getLogger(__name__)

XERO_AUTH_URL = "https://login.xero.com/identity/connect/authorize"
XERO_TOKEN_URL = "https://identity.xero.com/connect/token"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_API_URL = "https://api.xero.com/api.xro/2.0"


def _basic_auth_header() -> str:
    credentials = f"{settings.XERO_CLIENT_ID}:{settings.XERO_CLIENT_SECRET}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"


def get_authorization_url(state: str) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.XERO_CLIENT_ID,
        "redirect_uri": settings.XERO_REDIRECT_URI,
        "scope": " ".join(settings.XERO_SCOPES),
        "state": state,
    }
    return f"{XERO_AUTH_URL}?{urlencode(params)}"


def generate_state() -> str:
    return secrets.token_urlsafe(32)


def exchange_code_for_tokens(code: str) -> dict:
    response = requests.post(
        XERO_TOKEN_URL,
        headers={
            "Authorization": _basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.XERO_REDIRECT_URI,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def refresh_access_token(connection: XeroConnection) -> XeroConnection:
    response = requests.post(
        XERO_TOKEN_URL,
        headers={
            "Authorization": _basic_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        },
        data={
            "grant_type": "refresh_token",
            "refresh_token": connection.refresh_token,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    connection.access_token = data["access_token"]
    connection.refresh_token = data.get("refresh_token", connection.refresh_token)
    connection.token_expires_at = timezone.now() + timedelta(seconds=data.get("expires_in", 1800))
    connection.save()
    return connection


def get_tenant_id(access_token: str) -> tuple[str, str]:
    response = requests.get(
        XERO_CONNECTIONS_URL,
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    response.raise_for_status()
    connections = response.json()
    if not connections:
        return "", ""
    tenant = connections[0]
    return tenant.get("tenantId", ""), tenant.get("tenantName", "")


def save_connection(organisation, token_data: dict) -> XeroConnection:
    tenant_id, tenant_name = get_tenant_id(token_data["access_token"])
    connection, _ = XeroConnection.objects.update_or_create(
        organisation=organisation,
        defaults={
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token", ""),
            "token_expires_at": timezone.now()
            + timedelta(seconds=token_data.get("expires_in", 1800)),
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "is_connected": bool(tenant_id),
        },
    )
    return connection


def _ensure_valid_token(connection: XeroConnection) -> XeroConnection:
    if connection.token_expires_at and connection.token_expires_at <= timezone.now() + timedelta(
        minutes=5
    ):
        return refresh_access_token(connection)
    return connection


def create_invoice_for_payment(payment) -> XeroInvoice:
    """Create a Xero invoice for a successful payment."""
    organisation = payment.organisation
    connection = getattr(organisation, "xero_connection", None)

    invoice_record = XeroInvoice.objects.create(
        organisation=organisation,
        payment=payment,
        booking=payment.booking,
        contact_name=(
            payment.booking.child.parent.get_full_name() if payment.booking else "Customer"
        ),
        amount=payment.amount,
        status=XeroInvoice.Status.DRAFT,
    )

    if not connection or not connection.is_connected:
        invoice_record.sync_error = "Xero not connected"
        invoice_record.status = XeroInvoice.Status.ERROR
        invoice_record.save()
        return invoice_record

    try:
        connection = _ensure_valid_token(connection)
        description = payment.description or "Wraparound care booking"
        payload = {
            "Invoices": [
                {
                    "Type": "ACCREC",
                    "Contact": {"Name": invoice_record.contact_name},
                    "LineItems": [
                        {
                            "Description": description,
                            "Quantity": 1,
                            "UnitAmount": float(payment.amount),
                            "AccountCode": "200",
                        }
                    ],
                    "Status": "DRAFT",
                    "CurrencyCode": "GBP",
                }
            ]
        }
        response = requests.post(
            f"{XERO_API_URL}/Invoices",
            headers={
                "Authorization": f"Bearer {connection.access_token}",
                "Xero-tenant-id": connection.tenant_id,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            json=payload,
            timeout=30,
        )
        if response.status_code in (200, 201):
            data = response.json()
            xero_inv = data["Invoices"][0]
            invoice_record.xero_invoice_id = xero_inv["InvoiceID"]
            invoice_record.invoice_number = xero_inv.get("InvoiceNumber", "")
            invoice_record.status = XeroInvoice.Status.DRAFT
            invoice_record.last_synced_at = timezone.now()
        else:
            invoice_record.sync_error = response.text[:500]
            invoice_record.status = XeroInvoice.Status.ERROR
    except Exception as exc:
        logger.exception("Xero invoice sync failed")
        invoice_record.sync_error = str(exc)[:500]
        invoice_record.status = XeroInvoice.Status.ERROR

    invoice_record.save()
    return invoice_record
