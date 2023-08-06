from django.core.exceptions import PermissionDenied
from django_oso.auth import authorize_model
from rest_framework import filters


class OsoFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        action = getattr(view, "action", None)

        if action == "list":
            try:
                filters = authorize_model(request, queryset.model, action=action)
                return queryset.filter(filters)
            except PermissionDenied:
                return queryset.none()

        return queryset
