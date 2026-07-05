"""Render CMS page blocks for public and preview views."""

from bookings.models import Session
from django.utils.html import escape
from django.utils.safestring import mark_safe


def render_block(block, organisation, request=None):
    content = block.content or {}
    block_type = block.block_type

    if block_type == "hero":
        return _render_hero(content)
    if block_type == "rich_text":
        return _render_rich_text(content)
    if block_type == "features":
        return _render_features(content)
    if block_type == "cta":
        return _render_cta(content)
    if block_type == "image_text":
        return _render_image_text(content)
    if block_type == "contact_form":
        return _render_contact_form(content, organisation)
    if block_type == "session_list":
        return _render_session_list(organisation)
    if block_type == "pricing":
        return _render_pricing(organisation)
    if block_type == "faq":
        return _render_faq(content)
    if block_type == "testimonials":
        return _render_testimonials(content)
    return ""


def _render_hero(content):
    title = escape(content.get("title", ""))
    subtitle = escape(content.get("subtitle", ""))
    cta_text = escape(content.get("cta_text", "Book Now"))
    cta_url = escape(content.get("cta_url", "/sessions/"))
    return mark_safe(
        f'<section class="hero-block">'
        f"<h1>{title}</h1>"
        f"<p class='tagline'>{subtitle}</p>"
        f'<p><a href="{cta_url}" role="button">{cta_text}</a></p>'
        f"</section>"
    )


def _render_rich_text(content):
    body = content.get("body", "")
    return mark_safe(f'<section class="rich-text-block">{body}</section>')


def _render_features(content):
    items = content.get("items", [])
    html = '<section class="features-block"><div class="grid">'
    for item in items:
        html += (
            f"<article><h3>{escape(item.get('title', ''))}</h3>"
            f"<p>{escape(item.get('description', ''))}</p></article>"
        )
    html += "</div></section>"
    return mark_safe(html)


def _render_cta(content):
    title = escape(content.get("title", ""))
    text = escape(content.get("text", ""))
    btn = escape(content.get("button_text", "Get Started"))
    url = escape(content.get("button_url", "/register/"))
    return mark_safe(
        f'<section class="cta-block">'
        f"<h2>{title}</h2><p>{text}</p>"
        f'<a href="{url}" role="button">{btn}</a>'
        f"</section>"
    )


def _render_image_text(content):
    title = escape(content.get("title", ""))
    text = escape(content.get("text", ""))
    image_url = escape(content.get("image_url", ""))
    position = content.get("image_position", "left")
    img = f'<img src="{image_url}" alt="{title}">' if image_url else ""
    return mark_safe(
        f'<section class="image-text-block image-{position}">'
        f"{img}<div><h2>{title}</h2><p>{text}</p></div>"
        f"</section>"
    )


def _render_contact_form(content, organisation):
    title = escape(content.get("title", "Contact Us"))
    return mark_safe(
        f'<section class="contact-form-block" id="contact">'
        f"<h2>{title}</h2>"
        f'<div hx-get="/contact/" hx-trigger="revealed" hx-swap="innerHTML">'
        f"<p>Loading contact form…</p></div></section>"
    )


def _render_session_list(organisation):
    sessions = (
        Session.objects.filter(
            organisation=organisation,
            status=Session.Status.SCHEDULED,
        )
        .select_related("session_type", "site")
        .order_by("date", "start_time")[:10]
    )
    html = '<section class="session-list-block"><h2>Upcoming Sessions</h2><div class="grid">'
    for session in sessions:
        html += (
            f"<article><h3>{escape(session.session_type.name)}</h3>"
            f"<p>{session.date} · {session.start_time.strftime('%H:%M')} – "
            f"{session.end_time.strftime('%H:%M')}</p>"
            f"<p>{escape(session.site.name)} · "
            f"£{session.session_type.price} · "
            f"{session.spaces_remaining} spaces left</p>"
            f'<a href="/sessions/{session.pk}/book/" role="button" class="outline">'
            f"Book</a></article>"
        )
    html += "</div></section>"
    return mark_safe(html)


def _render_pricing(organisation):
    types = organisation.session_types.filter(is_active=True)
    html = '<section class="pricing-block"><h2>Our Prices</h2><div class="grid">'
    for st in types:
        html += (
            f"<article><h3>{escape(st.name)}</h3>"
            f"<p><strong>£{st.price}</strong> per session</p>"
            f"<p>{escape(st.description[:120])}</p></article>"
        )
    html += "</div></section>"
    return mark_safe(html)


def _render_faq(content):
    items = content.get("items", [])
    html = '<section class="faq-block"><h2>FAQ</h2>'
    for item in items:
        q = escape(item.get("question", ""))
        a = escape(item.get("answer", ""))
        html += f"<details><summary>{q}</summary><p>{a}</p></details>"
    html += "</section>"
    return mark_safe(html)


def _render_testimonials(content):
    items = content.get("items", [])
    html = '<section class="testimonials-block"><h2>What Parents Say</h2><div class="grid">'
    for item in items:
        html += (
            f'<blockquote><p>"{escape(item.get("quote", ""))}"</p>'
            f"<footer>— {escape(item.get('author', ''))}</footer></blockquote>"
        )
    html += "</div></section>"
    return mark_safe(html)
