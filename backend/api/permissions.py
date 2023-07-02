from rest_framework.permissions import BasePermission

class UserPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated