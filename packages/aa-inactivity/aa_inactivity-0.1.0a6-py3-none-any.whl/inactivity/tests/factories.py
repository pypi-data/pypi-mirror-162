import datetime as dt

import factory
import factory.fuzzy
from app_utils.testdata_factories import UserMainFactory

from django.utils.timezone import now

from ..models import InactivityPing, InactivityPingConfig, LeaveOfAbsence


class UserMainDefaultFactory(UserMainFactory):
    """A normal user with access to this app."""

    permissions__ = ["inactivity.basic_access"]


class UserMainManagerFactory(UserMainFactory):
    """A user who can manage loa requests."""

    permissions__ = ["inactivity.manage_leave"]


class LeaveOfAbsenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LeaveOfAbsence

    user = factory.SubFactory(UserMainDefaultFactory)
    approver = factory.SubFactory(UserMainManagerFactory)
    start = factory.fuzzy.FuzzyDateTime(
        start_dt=now() - dt.timedelta(days=3), force_microsecond=0
    )
    end = factory.LazyAttribute(
        lambda obj: factory.fuzzy.FuzzyDateTime(
            start_dt=obj.start, end_dt=now() + dt.timedelta(days=3), force_microsecond=0
        ).fuzz()
    )
    notes = factory.Faker("sentence")


class InactivityPingConfigFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InactivityPingConfig

    name = factory.Faker("city")
    days = 3
    text = factory.Faker("sentences")


class InactivityPingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = InactivityPing

    config = factory.SubFactory(InactivityPingConfigFactory)
    timestamp = factory.LazyFunction(now)
    user = factory.SubFactory(UserMainDefaultFactory)
