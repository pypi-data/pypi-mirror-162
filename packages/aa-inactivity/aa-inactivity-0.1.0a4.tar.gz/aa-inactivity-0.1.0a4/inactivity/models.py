import dhooks_lite
from multiselectfield import MultiSelectField

from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from allianceauth.authentication.models import State


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_access", "Can access this app"),
            ("manage_leave", "Can manage leave of absence requests"),
        )


class InactivityPingConfig(models.Model):
    name = models.CharField(
        max_length=48,
        unique=True,
        help_text=_("Internal name for the inactivity policy. Must be unique."),
    )
    days = models.PositiveIntegerField(
        help_text=_("The number of days the user must be inactive.")
    )
    text = models.TextField(
        help_text=_("The text of the message or notification sent to the end user.")
    )

    groups = models.ManyToManyField(
        Group,
        blank=True,
        help_text=_(
            "Groups subject to the inactivity policy. If empty, applies to all groups."
        ),
        related_name="+",
    )

    states = models.ManyToManyField(
        State,
        blank=True,
        help_text=_(
            "States subject to the inactivity policy. If empty, applies to all states."
        ),
        related_name="+",
    )

    class Meta:
        default_permissions = ()
        verbose_name = "inactivity policy"
        verbose_name_plural = "inactivity policies"

    def __str__(self):
        return _("inactivity policy: %(name)s") % {"name": self.name}

    def is_applicable_to(self, user: User) -> bool:
        is_applicable = True
        if self.groups.count() > 0:
            is_applicable &= self.groups.filter(user=user).count() > 0
        if self.states.count() > 0:
            is_applicable &= self.states.filter(userprofile=user.profile).count() > 0
        return is_applicable


class InactivityPing(models.Model):
    config = models.ForeignKey(InactivityPingConfig, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        default_permissions = ()

    def __str__(self):
        return _("ping [policy='%(config_name)s' user='%(user_name)s']") % {
            "config_name": self.config.name,
            "user_name": self.user.profile.main_character.character_name
            if self.user.profile.main_character
            else "None",
        }


class LeaveOfAbsence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    approver = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name="+"
    )
    start = models.DateField(help_text=_("The start of the leave of absence."))
    end = models.DateField(
        blank=True,
        null=True,
        help_text=_(
            "The end of the leave of absence. Leave blank for an indefinite leave."
        ),
    )
    notes = models.TextField(blank=True)

    class Meta:
        default_permissions = ()

    def save(self, *args, **kwargs):
        orig = LeaveOfAbsence.objects.filter(pk=self.pk).first()
        # find possible configs that could apply to the user, then alert based on that
        configs = []
        for config in InactivityPingConfig.objects.all():
            if config.is_applicable_to(self.user):
                configs.append(config)
        webhooks = Webhook.objects.filter(
            Q(ping_configs__in=configs) | Q(ping_configs=None), Q(is_active=True)
        )
        if self._state.adding:

            for webhook in webhooks:
                if str(Webhook.NOTIFICATION_TYPE_LOA_NEW) in webhook.notification_types:
                    if webhook.webhook_type == Webhook.WEBHOOK_TYPE_DISCORD:
                        hook = dhooks_lite.Webhook(webhook.url)
                        hook.execute(
                            "**%(user_name)s** has submitted a new leave of absence from **%(start)s** to **%(end)s**"
                            % {
                                "user_name": self.user.profile.main_character.character_name,
                                "start": self.start,
                                "end": self.end if self.end else "—",
                            }
                        )
        elif self.approver and not orig.approver:
            for webhook in webhooks:
                if (
                    str(Webhook.NOTIFICATION_TYPE_LOA_APPROVED)
                    in webhook.notification_types
                ):
                    if webhook.webhook_type == Webhook.WEBHOOK_TYPE_DISCORD:
                        hook = dhooks_lite.Webhook(webhook.url)
                        hook.execute(
                            "**%(user_name)s**'s leave of absence from **%(start)s** to **%(end)s** has been approved by **%(approver_name)s**"
                            % {
                                "user_name": self.user.profile.main_character.character_name,
                                "approver_name": self.approver.profile.main_character.character_name,
                                "start": self.start,
                                "end": self.end if self.end else "—",
                            }
                        )

        super(LeaveOfAbsence, self).save(*args, **kwargs)

    def __str__(self):
        return _("%(user_name)s's leave starting %(start)s") % {
            "start": self.start,
            "user_name": self.user.profile.main_character.character_name,
        }

    def clean(self):
        if self.end and self.end < self.start:
            raise ValidationError(_("End date must be after start date."))


class Webhook(models.Model):
    NOTIFICATION_TYPE_INACTIVE_USER = 1
    NOTIFICATION_TYPE_LOA_NEW = 10
    NOTIFICATION_TYPE_LOA_APPROVED = 11

    NOTIFICATION_TYPE_CHOICES = [
        (NOTIFICATION_TYPE_INACTIVE_USER, "Inactive User"),
        (NOTIFICATION_TYPE_LOA_NEW, "Leave of Absence - Created"),
        (NOTIFICATION_TYPE_LOA_APPROVED, "Leave of Absence - Approved"),
    ]

    WEBHOOK_TYPE_DISCORD = 1

    WEBHOOK_TYPE_CHOICES = [
        (WEBHOOK_TYPE_DISCORD, _("Discord Webhook")),
    ]

    name = models.CharField(
        max_length=64, unique=True, help_text="short name to identify this webhook"
    )

    notification_types = MultiSelectField(
        choices=NOTIFICATION_TYPE_CHOICES,
        help_text=("only notifications of the selected types are sent to this webhook"),
    )

    ping_configs = models.ManyToManyField(
        InactivityPingConfig,
        blank=True,
        help_text="The inactivity policies to alert for. If left blank, all policies are alerted for.",
    )

    url = models.CharField(
        max_length=255,
        unique=True,
        help_text=(
            "URL of this webhook, e.g. "
            "https://discordapp.com/api/webhooks/123456/abcdef"
        ),
    )
    webhook_type = models.IntegerField(
        choices=WEBHOOK_TYPE_CHOICES,
        default=WEBHOOK_TYPE_DISCORD,
        help_text="type of this webhook",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="whether notifications are currently sent to this webhook",
    )
