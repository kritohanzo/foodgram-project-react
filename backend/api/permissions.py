from rest_framework.permissions import BasePermission, SAFE_METHODS
    
class DisallowAny(BasePermission):
    def has_permission(self, request, view):
        return False
    
    def has_object_permission(self, request, view, obj):
        return False

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS or obj.author == request.user)
        