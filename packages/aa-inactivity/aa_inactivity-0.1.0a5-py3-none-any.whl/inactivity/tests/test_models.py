from app_utils.testdata_factories import UserFactory
from app_utils.testing import NoSocketsTestCase

from .factories import InactivityPingFactory


class TestInactivityPing(NoSocketsTestCase):
    def test_str_normal(self):
        # given
        ping = InactivityPingFactory()
        # when
        result = str(ping)
        # then
        self.assertIn(ping.user.last_name, result)

    def test_str_user_without_main(self):
        # given
        ping = InactivityPingFactory(user=UserFactory())
        # when
        result = str(ping)
        # then
        self.assertTrue(result)
