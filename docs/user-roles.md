# User roles

| Role | Access |
|------|--------|
| Super Admin | All organisations; franchise provisioning and applications (platform level) |
| Franchise Admin | All organisations within their franchise tenant |
| Organisation Admin | Full org management, CMS, billing, user administration |
| Site Manager | Sessions, children, bookings, CMS editing |
| Staff | Session management, register, check-in/out |
| Finance | Billing, Xero, payment reports, refunds |
| Parent | Public site, child profiles, online bookings |

Roles are defined on `accounts.models.User.Role` and enforced via decorators in `accounts/decorators.py`.
