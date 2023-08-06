from django.core.exceptions import PermissionDenied
from django_oso.auth import authorize
from django_oso.oso import Oso
from oso.exceptions import ForbiddenError
from rest_framework import permissions


class OsoPermissions(permissions.BasePermission):
    partial_update_is_update = True

    def has_permission(self, request, view):
        if hasattr(view, "action") and hasattr(view, "basename"):
            action = self._get_action(view.action)
            action = f"{action}-{view.basename}"
        else:
            action = request._request

        try:
            Oso.authorize_request(request.user, action)
            return True
        except ForbiddenError:
            return False

    def has_object_permission(self, request, view, obj):
        action = None

        if hasattr(view, "action"):
            action = self._get_action(view.action)

        try:
            authorize(request, obj, action=action)
            return True
        except PermissionDenied:
            return False

    def _get_action(self, action):
        return_action = action
        if self.partial_update_is_update and action == "partial_update":
            return_action = "update"
        return return_action
