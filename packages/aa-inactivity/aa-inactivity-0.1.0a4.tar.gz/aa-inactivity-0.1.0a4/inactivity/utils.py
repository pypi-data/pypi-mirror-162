from django.conf import settings
from django.contrib.auth.models import User

from allianceauth.notifications import notify


def notify_user(user_pk: int, message: str):
    if "aadiscordbot" in settings.INSTALLED_APPS:
        import aadiscordbot.tasks

        aadiscordbot.tasks.send_direct_message_by_user_id.delay(user_pk, message)
    else:
        notify(
            User.objects.get(pk=user_pk), "Inactivity Notification", message, "danger"
        )
