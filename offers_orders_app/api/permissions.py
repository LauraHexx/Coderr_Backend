
from rest_framework.permissions import BasePermission


class IsBusinessUser(BasePermission):
    """
    Allows access only to users of type 'business'.
    """

    def has_permission(self, request, view):
        return request.user.type == 'business'


class IsOfferCreator(BasePermission):
    """
    Allows access only to the creator of the offer.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
