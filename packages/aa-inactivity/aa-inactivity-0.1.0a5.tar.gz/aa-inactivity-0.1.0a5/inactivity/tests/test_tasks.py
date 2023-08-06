import datetime as dt
from unittest.mock import patch

from app_utils.testdata_factories import UserMainFactory
from app_utils.testing import NoSocketsTestCase

from django.utils.timezone import now

from memberaudit.tests.testdata.factories import (
    create_character_from_user,
    create_online_status,
)

from ..tasks import check_inactivity_for_user
from .factories import (
    InactivityPingConfigFactory,
    InactivityPingFactory,
    LeaveOfAbsenceFactory,
)

TASKS_PATH = "inactivity.tasks"


@patch(TASKS_PATH + ".send_inactivity_ping")
class TestCheckInactivityForUser(NoSocketsTestCase):
    def test_should_ping_for_inactive_user(self, mock_send_inactivity_ping):
        # given
        user = UserMainFactory()
        character = create_character_from_user(user=user)
        last_login = now() - dt.timedelta(days=4)
        create_online_status(
            character=character,
            last_login=last_login,
            last_logout=last_login + dt.timedelta(hours=4),
        )
        InactivityPingConfigFactory(days=3)
        # when
        check_inactivity_for_user(user_pk=user.pk)
        # then
        self.assertTrue(mock_send_inactivity_ping.called)

    def test_should_not_ping_for_active_user(self, mock_send_inactivity_ping):
        # given
        user = UserMainFactory()
        character = create_character_from_user(user=user)
        last_login = now() - dt.timedelta(days=1)
        create_online_status(
            character=character,
            last_login=last_login,
            last_logout=last_login + dt.timedelta(hours=4),
        )
        InactivityPingConfigFactory(days=3)
        # when
        check_inactivity_for_user(user_pk=user.pk)
        # then
        self.assertFalse(mock_send_inactivity_ping.called)

    def test_should_not_ping_for_user_without_character(
        self, mock_send_inactivity_ping
    ):
        # given
        user = UserMainFactory()
        InactivityPingConfigFactory(days=3)
        # when
        check_inactivity_for_user(user_pk=user.pk)
        # then
        self.assertFalse(mock_send_inactivity_ping.called)

    def test_should_not_ping_for_excused_user(self, mock_send_inactivity_ping):
        # given
        user = UserMainFactory()
        character = create_character_from_user(user=user)
        last_login = now() - dt.timedelta(days=4)
        create_online_status(
            character=character,
            last_login=last_login,
            last_logout=last_login + dt.timedelta(hours=4),
        )
        LeaveOfAbsenceFactory(
            user=user, start=last_login, end=now() + dt.timedelta(days=3)
        )
        InactivityPingConfigFactory(days=3)
        # when
        check_inactivity_for_user(user_pk=user.pk)
        # then
        self.assertFalse(mock_send_inactivity_ping.called)

    def test_should_not_ping_when_already_pinged(self, mock_send_inactivity_ping):
        # given
        user = UserMainFactory()
        character = create_character_from_user(user=user)
        last_login = now() - dt.timedelta(days=4)
        create_online_status(
            character=character,
            last_login=last_login,
            last_logout=last_login + dt.timedelta(hours=4),
        )
        config = InactivityPingConfigFactory(days=3)
        InactivityPingFactory(user=user, config=config)
        # when
        check_inactivity_for_user(user_pk=user.pk)
        # then
        self.assertFalse(mock_send_inactivity_ping.called)
