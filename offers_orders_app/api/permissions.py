from rest_framework.permissions import BasePermission


class IsOrderBusinessOwner(BasePermission):
    """
    Allows access only to the business user of the order.
    """

    def has_object_permission(self, request, view, obj):
        return getattr(obj, "business_user", None) == request.user
