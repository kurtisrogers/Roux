from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from typing import Literal

from bookings.models import Session
from django.db.models import Q
from django.utils import timezone

from programme.models import Programme, ScheduleEvent, WeekPack, WeekPackBlock


@dataclass
class ResolvedBlock:
    start_time: time
    end_time: time
    activity: object | None
    label: str
    notes: str
    source: Literal["week_a", "week_b", "single", "merged"]
    is_running_period: bool
    week_label: str = ""

    @property
    def display_name(self) -> str:
        if self.label:
            return self.label
        if self.activity:
            return self.activity.name
        return "Break"


def week_pack_for_date(programme: Programme, target: date) -> tuple[WeekPack, Literal["week_a", "week_b"]]:
    weeks_since_anchor = (target - programme.anchor_date).days // 7
    is_anchor_week = weeks_since_anchor % 2 == 0
    use_a = is_anchor_week if programme.first_week == Programme.FirstWeek.A else not is_anchor_week
    if use_a:
        return programme.week_a_pack, "week_a"
    return programme.week_b_pack, "week_b"


def _closure_matches(
    event: ScheduleEvent,
    target: date,
    *,
    site_id: int | None,
    session_type_id: int | None,
) -> bool:
    if event.kind != ScheduleEvent.Kind.CLOSURE:
        return False
    if not event.start_date or not event.end_date:
        return False
    if not (event.start_date <= target <= event.end_date):
        return False
    if event.site_id and site_id and event.site_id != site_id:
        return False
    return not (
        event.session_type_id
        and session_type_id
        and event.session_type_id != session_type_id
    )


def is_date_closed(
    organisation,
    target: date,
    *,
    site_id: int | None = None,
    session_type_id: int | None = None,
    programme: Programme | None = None,
) -> bool:
    """Return True if wraparound care is closed on this date for the given scope."""
    events = ScheduleEvent.objects.filter(
        organisation=organisation,
        kind=ScheduleEvent.Kind.CLOSURE,
        start_date__lte=target,
        end_date__gte=target,
    )
    if programme:
        events = events.filter(Q(programme=programme) | Q(programme__isnull=True))
    for event in events:
        if _closure_matches(event, target, site_id=site_id, session_type_id=session_type_id):
            return True
    return False


def _block_from_week_pack_block(block: WeekPackBlock, source: Literal["week_a", "week_b"]) -> ResolvedBlock:
    return ResolvedBlock(
        start_time=block.start_time,
        end_time=block.end_time,
        activity=block.activity,
        label=block.label,
        notes=block.notes,
        source=source,
        is_running_period=block.is_running_period,
        week_label="Week A" if source == "week_a" else "Week B",
    )


def _block_from_single(event: ScheduleEvent) -> ResolvedBlock:
    return ResolvedBlock(
        start_time=event.start_time or time(0, 0),
        end_time=event.end_time or time(23, 59),
        activity=event.activity,
        label=event.label,
        notes=event.notes,
        source="single",
        is_running_period=bool(event.activity),
        week_label="Override",
    )


def _times_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    return start_a < end_b and start_b < end_a


def resolve_programme(programme: Programme, target: date) -> list[ResolvedBlock] | None:
    if target < programme.start_date or target > programme.end_date:
        return None

    site_id = programme.site_id
    session_type_id = programme.session_type_id
    if is_date_closed(
        programme.organisation,
        target,
        site_id=site_id,
        session_type_id=session_type_id,
        programme=programme,
    ):
        return None

    singles = list(
        ScheduleEvent.objects.filter(
            programme=programme,
            kind=ScheduleEvent.Kind.SINGLE,
            date=target,
        ).order_by("sort_order", "start_time")
    )

    if singles and any(event.replaces_day for event in singles):
        return [_block_from_single(event) for event in singles]

    week_pack, source = week_pack_for_date(programme, target)
    base_blocks = [
        _block_from_week_pack_block(block, source)
        for block in WeekPackBlock.objects.filter(
            week_pack=week_pack,
            weekday=target.weekday(),
        ).select_related("activity")
    ]

    if not singles:
        return base_blocks

    merged: list[ResolvedBlock] = []
    for base in base_blocks:
        overlapped = False
        for single in singles:
            if single.start_time and single.end_time and _times_overlap(
                base.start_time, base.end_time, single.start_time, single.end_time
            ):
                overlapped = True
                break
        if not overlapped:
            block = ResolvedBlock(
                start_time=base.start_time,
                end_time=base.end_time,
                activity=base.activity,
                label=base.label,
                notes=base.notes,
                source="merged",
                is_running_period=base.is_running_period,
                week_label=base.week_label,
            )
            merged.append(block)

    for single in singles:
        if single.start_time:
            merged.append(_block_from_single(single))

    merged.sort(key=lambda b: b.start_time)
    return merged


def find_published_programme(
    organisation,
    target: date,
    *,
    site_id: int | None,
    session_type_id: int,
) -> Programme | None:
    candidates = Programme.objects.filter(
        organisation=organisation,
        session_type_id=session_type_id,
        status=Programme.Status.PUBLISHED,
        start_date__lte=target,
        end_date__gte=target,
    ).select_related("week_a_pack", "week_b_pack", "site", "session_type")

    best: Programme | None = None
    for programme in candidates:
        if programme.site_id and site_id and programme.site_id != site_id:
            continue
        if programme.site_id and not site_id:
            continue
        if best is None or programme.site_id and not best.site_id:
            best = programme
    return best


def resolve_for_session(session: Session) -> list[ResolvedBlock] | None:
    programme = find_published_programme(
        session.organisation,
        session.date,
        site_id=session.site_id,
        session_type_id=session.session_type_id,
    )
    if not programme:
        return None
    return resolve_programme(programme, session.date)


def week_label_for_date(programme: Programme, target: date) -> str:
    _, source = week_pack_for_date(programme, target)
    return "Week A" if source == "week_a" else "Week B"


def publish_programme(programme: Programme) -> Programme:
    programme.status = Programme.Status.PUBLISHED
    programme.published_at = timezone.now()
    programme.full_clean()
    programme.save(update_fields=["status", "published_at", "updated_at"])
    return programme

def duplicate_week_pack(source: WeekPack, new_name: str) -> WeekPack:
    duplicate = WeekPack.objects.create(
        organisation=source.organisation,
        name=new_name,
        description=source.description,
    )
    for block in source.blocks.all():
        WeekPackBlock.objects.create(
            week_pack=duplicate,
            weekday=block.weekday,
            start_time=block.start_time,
            end_time=block.end_time,
            activity=block.activity,
            label=block.label,
            notes=block.notes,
            sort_order=block.sort_order,
            is_running_period=block.is_running_period,
        )
    return duplicate
