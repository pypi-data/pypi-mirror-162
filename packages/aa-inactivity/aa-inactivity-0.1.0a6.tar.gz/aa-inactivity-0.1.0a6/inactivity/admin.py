from django.contrib import admin

from .models import InactivityPing, InactivityPingConfig, LeaveOfAbsence, Webhook

# Register your models here.


@admin.register(InactivityPingConfig)
class InactivityPingConfigAdmin(admin.ModelAdmin):
    list_display = ("name", "days", "_groups", "_states")
    filter_horizontal = ("groups", "states")

    def _groups(self, obj):
        return ", ".join(obj.groups.values_list("name", flat=True))

    def _states(self, obj):
        return (", ".join(obj.states.values_list("name", flat=True)),)


@admin.register(InactivityPing)
class InactivityPingAdmin(admin.ModelAdmin):
    list_display = ("config", "user", "timestamp")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


def approve_leaveofabsence(modeladmin, request, queryset):
    queryset.update(approver=request.user)


approve_leaveofabsence.short_description = "Approve selected leave of absences"


@admin.register(LeaveOfAbsence)
class LeaveOfAbsenceAdmin(admin.ModelAdmin):
    list_display = ("user", "start", "end", "approver")
    ordering = ("-start",)
    actions = [approve_leaveofabsence]


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("name", "webhook_type", "url")
    filter_horizontal = ("ping_configs",)
