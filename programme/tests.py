from datetime import date, time, timedelta

import pytest
from django.core.exceptions import ValidationError

from programme.models import Activity, Programme, ScheduleEvent, WeekPack, WeekPackBlock
from programme.services import (
    duplicate_week_pack,
    is_date_closed,
    resolve_programme,
    week_pack_for_date,
)
from tests.factories import OrganisationFactory, SessionTypeFactory, SiteFactory


@pytest.mark.django_db
class TestWeekAlternation:
    def _build_programme(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        week_a = WeekPack.objects.create(organisation=org, name="Week A")
        week_b = WeekPack.objects.create(organisation=org, name="Week B")
        anchor = date(2026, 9, 7)  # Monday
        programme = Programme.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            name="Autumn term",
            start_date=anchor,
            end_date=anchor + timedelta(days=60),
            week_a_pack=week_a,
            week_b_pack=week_b,
            anchor_date=anchor,
            first_week=Programme.FirstWeek.A,
        )
        return programme, week_a, week_b, anchor

    def test_alternates_a_and_b(self):
        programme, week_a, week_b, anchor = self._build_programme()
        pack0, source0 = week_pack_for_date(programme, anchor)
        pack7, source7 = week_pack_for_date(programme, anchor + timedelta(days=7))
        assert pack0 == week_a and source0 == "week_a"
        assert pack7 == week_b and source7 == "week_b"


@pytest.mark.django_db
class TestResolution:
    def test_closure_returns_none(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        week_a = WeekPack.objects.create(organisation=org, name="Week A")
        week_b = WeekPack.objects.create(organisation=org, name="Week B")
        start = date(2026, 6, 1)
        programme = Programme.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            name="Summer",
            start_date=start,
            end_date=start + timedelta(days=30),
            week_a_pack=week_a,
            week_b_pack=week_b,
            anchor_date=start,
        )
        ScheduleEvent.objects.create(
            organisation=org,
            programme=programme,
            kind=ScheduleEvent.Kind.CLOSURE,
            start_date=start + timedelta(days=5),
            end_date=start + timedelta(days=5),
            label="Inset day",
        )
        target = start + timedelta(days=5)
        assert resolve_programme(programme, target) is None
        assert is_date_closed(org, target, site_id=site.pk, session_type_id=st.pk)

    def test_replace_day_override(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        activity = Activity.objects.create(organisation=org, name="Trip")
        week_a = WeekPack.objects.create(organisation=org, name="Week A")
        week_b = WeekPack.objects.create(organisation=org, name="Week B")
        target = date(2026, 6, 2)  # Tuesday
        WeekPackBlock.objects.create(
            week_pack=week_a,
            weekday=target.weekday(),
            start_time=time(15, 30),
            end_time=time(16, 0),
            activity=activity,
        )
        programme = Programme.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            name="Summer",
            start_date=target - timedelta(days=7),
            end_date=target + timedelta(days=7),
            week_a_pack=week_a,
            week_b_pack=week_b,
            anchor_date=target - timedelta(days=7),
        )
        ScheduleEvent.objects.create(
            organisation=org,
            programme=programme,
            kind=ScheduleEvent.Kind.SINGLE,
            date=target,
            start_time=time(10, 0),
            end_time=time(15, 0),
            activity=activity,
            label="Coach trip",
            replaces_day=True,
        )
        blocks = resolve_programme(programme, target)
        assert blocks is not None
        assert len(blocks) == 1
        assert blocks[0].label == "Coach trip"
        assert blocks[0].source == "single"


@pytest.mark.django_db
class TestPublish:
    def test_overlapping_published_programmes_rejected(self):
        org = OrganisationFactory()
        site = SiteFactory(organisation=org)
        st = SessionTypeFactory(organisation=org)
        week_a = WeekPack.objects.create(organisation=org, name="Week A")
        week_b = WeekPack.objects.create(organisation=org, name="Week B")
        start = date(2026, 4, 1)
        first = Programme.objects.create(
            organisation=org,
            site=site,
            session_type=st,
            name="Term 1",
            start_date=start,
            end_date=start + timedelta(days=30),
            week_a_pack=week_a,
            week_b_pack=week_b,
            anchor_date=start,
            status=Programme.Status.PUBLISHED,
        )
        assert first.pk
        second = Programme(
            organisation=org,
            site=site,
            session_type=st,
            name="Term 1 duplicate",
            start_date=start,
            end_date=start + timedelta(days=20),
            week_a_pack=week_a,
            week_b_pack=week_b,
            anchor_date=start,
            status=Programme.Status.PUBLISHED,
        )
        with pytest.raises(ValidationError):
            second.full_clean()


@pytest.mark.django_db
class TestWeekPackDuplicate:
    def test_duplicate_copies_blocks(self):
        org = OrganisationFactory()
        pack = WeekPack.objects.create(organisation=org, name="Week A")
        activity = Activity.objects.create(organisation=org, name="Craft")
        WeekPackBlock.objects.create(
            week_pack=pack,
            weekday=0,
            start_time=time(15, 0),
            end_time=time(15, 30),
            activity=activity,
        )
        copy = duplicate_week_pack(pack, "Week B")
        assert copy.blocks.count() == 1
        assert copy.blocks.first().activity == activity
