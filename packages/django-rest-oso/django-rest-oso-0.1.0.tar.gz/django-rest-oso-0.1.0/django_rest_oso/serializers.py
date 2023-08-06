from django_oso.oso import Oso
from rest_framework import serializers


class PermissionsField(serializers.ReadOnlyField):
    def get_attribute(self, instance):
        return instance

    def to_representation(self, value):
        request = self.context.get("request")

        if request:
            return Oso.authorized_actions(request.user, value)

        return []
