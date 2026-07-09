# Mobile API

JWT-authenticated REST API at `/api/v1/` for iOS and Android clients.

## Authentication

```bash
# Obtain access + refresh tokens
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "parent1", "password": "parent123"}'

# Refresh an expired access token
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

Include the access token on requests: `Authorization: Bearer <access_token>`

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/me/` | Current user profile |
| GET | `/api/v1/sessions/` | List scheduled sessions |
| GET | `/api/v1/sessions/upcoming/` | Upcoming sessions only |
| GET/POST | `/api/v1/children/` | List or create children for the logged-in parent |
| GET/POST | `/api/v1/bookings/` | List or create bookings |
| POST | `/api/v1/bookings/<id>/cancel/` | Cancel a booking |

Sessions include `programme_blocks` when a programme is published for the session date.

## Roadmap

- Stripe payment completion in API
- Push notification registration
- Staff check-in/out endpoints
