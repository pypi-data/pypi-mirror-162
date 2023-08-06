from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook, UrlHook

from . import urls


class LeaveOfAbsenceMenuItem(MenuItemHook):
    def __init__(self):
        MenuItemHook.__init__(
            self,
            _("Leave of Absence"),
            "fas fa-business-time fa-fw",
            "inactivity:index",
            navactive=["inactivity:"],
        )

    def render(self, request):
        if request.user.has_perm("inactivity.basic_access"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register("menu_item_hook")
def register_menu():
    return LeaveOfAbsenceMenuItem()


@hooks.register("url_hook")
def register_urls():
    return UrlHook(urls, "inactivity", r"^inactivity/")
