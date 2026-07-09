# Public site & CMS

Each organisation's public website is built from the dashboard CMS. Block types include hero, rich text, features, CTA, FAQ, testimonials, session list, pricing, and contact form. Pages support drag-and-drop reordering with SortableJS.

## Parent booking flow

1. Parent registers or logs in at the public site
2. Browses sessions at `/sessions/` or the calendar at `/sessions/calendar/`
3. Selects a child and payment method (Stripe card or childcare voucher)
4. Receives confirmation email on successful booking

## Programme on booking

When a programme is published, parents see the day's activity blocks on the session booking page before confirming.

## CMS extension

To add a block type:

1. Add to `PageBlock.BlockType` in `cms/models.py`
2. Create a form in `cms/block_forms.py`
3. Render in `cms/block_renderer.py`

## Organisation resolution

In development, the default organisation is resolved via `DEFAULT_ORGANISATION_SLUG`. In production, subdomain routing resolves the organisation within the franchise hostname.
