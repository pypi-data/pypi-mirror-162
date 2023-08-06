import factory
import factory.fuzzy
from app_utils.testdata_factories import UserMainFactory

from django.utils.timezone import now

from ..models import InactivityPing, InactivityPingConfig


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
    user = factory.SubFactory(UserMainFactory)
