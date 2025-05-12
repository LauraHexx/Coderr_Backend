from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """
    Allows access only to the creator.
    """

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
