from rest_framework import permissions


class ReadOnlyOrOwnerUpdateOrAdmin(permissions.BasePermission):
    """
    - SAFE_METHODS: everyone allowed
    - PATCH/PUT: only owner or admin
    - DELETE: only admin
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method in ['PATCH', 'PUT']:
            return obj.user == request.user or request.user.is_staff

        if request.method == 'DELETE':
            return request.user.is_staff

        return False
