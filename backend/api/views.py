from rest_framework.viewsets import ModelViewSet, GenericViewSet
from users.models import User, Subscribe
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.permissions import DisallowAny
from rest_framework.exceptions import NotFound
from django.contrib.auth import update_session_auth_hash
from recipes.models import Ingredient, Tag, Recipe
from django.shortcuts import get_object_or_404
from api.serializers import IngredientSerializer, TagSerializer, RecipeSerializer
from rest_framework.filters import SearchFilter
from rest_framework.viewsets import mixins

from djoser import signals, utils
from djoser.compat import get_user_email
from djoser.conf import settings

class CustomDjoserUserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = settings.SERIALIZERS.user
    queryset = User.objects.all()
    permission_classes = settings.PERMISSIONS.user
    lookup_field = settings.USER_ID_FIELD

    def get_queryset(self):
        if self.action == "subscribe" or self.action == "subscriptions":
            return Subscribe.objects.all()
        return super().get_queryset()

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = settings.PERMISSIONS.user_create
        elif self.action == "list":
            self.permission_classes = settings.PERMISSIONS.user_list
        elif self.action == "set_password":
            self.permission_classes = settings.PERMISSIONS.set_password
        elif self.action == "me":
            self.permission_classes = settings.PERMISSIONS.user_me
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        elif self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        elif self.action == "me":
            return settings.SERIALIZERS.current_user
        elif self.action == "subscribe" or self.action == "subscriptions":
            return settings.SERIALIZERS.subscribe

        return self.serializer_class

    def get_instance(self):
        print(self.request.user)
        return self.request.user

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)
        

    @action(["post"], detail=False)
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()

        if settings.PASSWORD_CHANGED_EMAIL_CONFIRMATION:
            context = {"user": self.request.user}
            to = [get_user_email(self.request.user)]
            settings.EMAIL.password_changed_confirmation(self.request, context).send(to)

        if settings.LOGOUT_ON_PASSWORD_CHANGE:
            utils.logout_user(self.request)
        elif settings.CREATE_SESSION_ON_LOGIN:
            update_session_auth_hash(self.request, self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(["POST", "DELETE"], detail=False, url_path=r"(?P<id>\w+)/subscribe")
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user == author:
                 return Response({"errors": "Вы не можете подписаться на себя"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                instance = Subscribe.objects.create(subscriber=request.user, author=author)
            except:
                return Response({"errors": "Вы уже подписаны на автора"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = self.get_serializer(instance)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            subscribe = Subscribe.objects.filter(subscriber=request.user, author=author)
            if subscribe.exists():
                subscribe.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"errors": "Вы не были подписаны на автора"}, status=status.HTTP_400_BAD_REQUEST)

    
    @action(["GET"], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_object = Subscribe.objects.filter(subscriber=request.user)
        return self.list(request, *args, **kwargs)

class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [SearchFilter]
    search_fields = ['^name']

class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class RecipeViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, GenericViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    