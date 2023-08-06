from django.urls import path

from . import views

app_name = "inactivity"

urlpatterns = [
    path("", views.index, name="index"),
    path("manage", views.manage, name="manage_requests"),
    path("loa_requests", views.list_loa_requests, name="list_loa_requests"),
    path(
        "loa_requests/pending",
        views.list_pending_loa_requests,
        name="list_pending_loa_requests",
    ),
    path("loa_requests/create", views.create_loa_request, name="create_loa_request"),
    path(
        "loa_requests/<int:request_id>/cancel",
        views.cancel_loa_request,
        name="cancel_loa_request",
    ),
    path(
        "loa_requests/<int:request_id>/approve",
        views.approve_loa_request,
        name="approve_loa_request",
    ),
    path(
        "loa_requests/<int:request_id>",
        views.view_loa_request,
        name="view_loa_request",
    ),
]
