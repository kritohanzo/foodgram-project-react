from .serializers import UserSerializer
from rest_framework.viewsets import ModelViewSet
from users.models import User
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from api.permissions import UserPermissions

class UserViewSet(ModelViewSet):
    """Вьюсет пользователя."""

    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [UserPermissions]
    # lookup_field = "username"
    # search_fields = ["username"]
    # filter_backends = [SearchFilter]
    # http_method_names = [
    #     "post",
    #     "patch",
    #     "get",
    #     "delete",
    # ]

    @action(
        methods=[
            "GET",
        ],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        user = request.user
        if user.check_password(request.data.get("current_password")):
            user.set_password(request.data.get("new_password"))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return  Response({"error": "password not corrected"}, status=status.HTTP_400_BAD_REQUEST)