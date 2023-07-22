from rest_framework.permissions import BasePermission, SAFE_METHODS


class DisallowAny(BasePermission):
    """Кастомное ограничение, запрещающее любые запросы."""

    def has_permission(self, request, view):
        return False

    def has_object_permission(self, request, view, obj):
        return False


class IsAuthorOrReadOnly(BasePermission):
    """
    Кастомное ограничение, разрешающее любой запрос к эндпоинту
    и запрещающий запросы к объекту в том случае,
    если инициатор запроса - не автор объекта.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or obj.author == request.user
