"""Shared test factories."""

from datetime import date

import factory
from accounts.models import User
from bookings.models import Child, SessionType
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from organisations.models import Organisation, Site

UserModel = get_user_model()


class OrganisationFactory(DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Sequence(lambda n: f"Test Club {n}")
    slug = factory.Sequence(lambda n: f"test-club-{n}")
    email = factory.LazyAttribute(lambda o: f"hello@{o.slug}.example")
    city = "Manchester"
    postcode = "M1 1AA"


class SiteFactory(DjangoModelFactory):
    class Meta:
        model = Site

    organisation = factory.SubFactory(OrganisationFactory)
    name = "Main Site"
    slug = "main"
    city = "Manchester"
    capacity = 30


class UserFactory(DjangoModelFactory):
    class Meta:
        model = UserModel
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@example.com")
    first_name = "Test"
    last_name = "User"
    role = User.Role.PARENT

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        raw = extracted or "testpass123"
        self.set_password(raw)
        if create:
            self.save()


class SessionTypeFactory(DjangoModelFactory):
    class Meta:
        model = SessionType

    organisation = factory.SubFactory(OrganisationFactory)
    name = "After School Club"
    price = "12.00"
    capacity = 20


class ChildFactory(DjangoModelFactory):
    class Meta:
        model = Child

    parent = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)
    first_name = "Alex"
    last_name = "Smith"
    date_of_birth = date(2018, 6, 1)
    emergency_contact_name = "Parent"
    emergency_contact_phone = "07000000000"
