# Operations module

The `operations` app extends the dashboard with day-to-day club management workflows beyond core bookings.

## Capabilities

| Feature | Description |
|---------|-------------|
| Session register | Live check-in/out, authorised collectors, walk-ins, today's programme |
| Waitlist | Auto-promote when spaces open; parent notifications |
| Childcare vouchers | Voucher balances, redemption at checkout |
| Recurring bookings | Standing weekly bookings applied via management command |
| Safeguarding | Concern logging, assignment, and staff notifications |
| Analytics | Attendance, revenue, and occupancy metrics |
| Staff rota | Shift scheduling per site |
| Visitors | Sign-in/sign-out log |
| Medication | Administration records |
| Staff compliance | DBS, first aid, safeguarding certificate tracking |

## Key dashboard routes

| Route | Purpose |
|-------|---------|
| `/dashboard/sessions/<id>/register/` | Live register |
| `/dashboard/waitlist/` | Waiting list management |
| `/dashboard/vouchers/` | Childcare voucher admin |
| `/dashboard/recurring/` | Recurring booking rules |
| `/dashboard/calendar/` | Staff booking calendar |
| `/dashboard/safeguarding/` | Safeguarding concerns |
| `/dashboard/analytics/` | Operations analytics |
| `/dashboard/rota/` | Staff rota |
| `/dashboard/visitors/` | Visitor sign-in |
| `/dashboard/medication/` | Medication administration records |

## Services

Business logic lives in `operations/services.py` — register rows, walk-ins, collector checkout, late fees, waitlist promotion, voucher redemption, and analytics aggregation.
