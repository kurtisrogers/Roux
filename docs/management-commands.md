# Management commands

| Command | Purpose |
|---------|---------|
| `seed_demo` | Populate demo organisation, users, sessions, vouchers, and sample data |
| `provision_franchise` | Create an isolated franchise tenant with database and admin user |
| `apply_recurring_bookings` | Materialise recurring booking rules into session bookings (run daily via cron) |
| `send_session_reminders` | Email staff reminders for upcoming sessions |
| `send_dbs_reminders` | Alert staff when DBS certificates are nearing expiry |
| `sync_mis` | Stub for MIS (school information system) pupil sync |

## Examples

```bash
python manage.py seed_demo
python manage.py apply_recurring_bookings
python manage.py send_dbs_reminders
```
