# Programme planner

The `programme` app provides term-time activity planning with Week A/B alternation, closures, and day-level overrides.

## Concepts

| Model | Purpose |
|-------|---------|
| `Activity` | Catalogue item (sport, creative, quiet, outdoor, food) |
| `WeekPack` | Reusable week template with time-slot blocks |
| `Programme` | Term programme linking Week A and Week B packs |
| `ScheduleEvent` | Closures, overrides, and replace-day trips |

## Resolution engine

`programme/services.py` resolves the timetable for any session date:

1. Check for closure events
2. Apply day-level overrides or replace-day trips
3. Fall back to Week A/B alternation from the published programme

Resolved blocks appear on the session register, session detail, parent booking page, and mobile API.

## Dashboard routes

| Route | Purpose |
|-------|---------|
| `/dashboard/programme/activities/` | Activity catalogue |
| `/dashboard/programme/week-packs/` | Week pack templates |
| `/dashboard/programme/` | Term programmes |
| `/dashboard/programme/calendar/` | Programme calendar |
| `/dashboard/programme/day/<date>/` | Day editor (overrides, trips) |
| `/dashboard/programme/closures/` | Closure periods |

## Publishing

Programmes must be published before they take effect. `publish_programme()` validates date ranges and prevents overlapping published programmes.
