
from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """
    Allows access only to users of type 'business'.
    """

    def has_permission(self, request, view):
        user = request.user
        profile = getattr(user, "userprofile", None)
        return profile is not None and profile.type == "business"


class IsCustomerUser(BasePermission):
    """
    Allows access only to users of type 'customer'.
    """

    def has_permission(self, request, view):
        user = request.user
        profile = getattr(user, "userprofile", None)
        return profile is not None and profile.type == "customer"


class IsOwner(BasePermission):
    """
    Allows access only to the creator.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
