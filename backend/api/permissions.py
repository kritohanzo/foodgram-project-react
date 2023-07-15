from rest_framework.permissions import BasePermission

class UserPermissions(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated
    
class DisallowAny(BasePermission):
    def has_permission(self, request, view):
        return False
    
    def has_object_permission(self, request, view, obj):
        return False