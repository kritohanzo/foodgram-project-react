from typing import Optional, Type

from djoser import utils
from djoser.serializers import (SetPasswordSerializer, TokenCreateSerializer,
                                TokenSerializer, UserCreateSerializer,)
from rest_framework import generics, status
from rest_framework.decorators import action
from rest_framework.exceptions import NotAuthenticated
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,)
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.viewsets import (GenericViewSet, ModelViewSet,
                                     ReadOnlyModelViewSet, mixins,)

from django.db.models import Count
from django.db.utils import IntegrityError
from django.shortcuts import HttpResponse, get_object_or_404

from api.permissions import IsAuthorOrReadOnly
from api.serializers import (CreateUpdateRecipeSerializer,
                             FullRecipeSerializer, IngredientSerializer,
                             ShortRecipeSerializer, SubscribeSerializer,
                             TagSerializer, UserSerializer,)
from core.utils import generate_text_of_shopping_cart
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from users.models import Subscribe, User


class MultiSerializerViewSetMixin:
    """Миксин для выбора нужного сериализатора из `serializer_classes`."""

    serializer_classes: Optional[dict[str, Type[Serializer]]] = None

    def get_serializer_class(self):
        try:
            return self.serializer_classes[self.action]
        except KeyError:
            return super().get_serializer_class()


class UserViewSet(
    MultiSerializerViewSetMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Кастомный вьюсет Djoser для работы с пользователями.

    Предоставляет пользователям возможность регистрации аккаунта,
    получения информации о себе/пользователях/пользователе,
    смены своего пароля, подписки/отписки на/от другого пользователя,
    просмотра своих подписок.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    serializer_classes = {
        "create": UserCreateSerializer,
        "list": UserSerializer,
        "retrieve": UserSerializer,
        "me": UserSerializer,
        "set_password": SetPasswordSerializer,
        "subscribe": SubscribeSerializer,
        "subscriptions": SubscribeSerializer,
    }

    def get_queryset(self):
        if self.action == "subscribe" or self.action == "subscriptions":
            return (
                Subscribe.objects.filter(subscriber=self.request.user)
                .select_related("author", "subscriber")
                .annotate(recipes_count=Count("author__recipes"))
            )
        return super().get_queryset()

    def get_permissions(self):
        if self.action == "create" or self.action == "list":
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_instance(self):
        return self.request.user

    @action(["get"], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """Функция-обработчик для эндпоинта "/users/me/".

        Позволяет пользователям получать информацию о себе.
        """
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)

    @action(
        ["post"],
        detail=False,
        url_name="set_password",
        permission_classes=[IsAuthenticated],
    )
    def set_password(self, request, *args, **kwargs):
        """Функция-обработчик для эндпоинта "/users/set_password/".

        Позволяет пользователям менять пароль.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        ["POST", "DELETE"],
        detail=False,
        url_path=r"(?P<id>\w+)/subscribe",
        permission_classes=[IsAuthenticated],
    )
    def subscribe(self, request, id):
        """Функция-обработчик для эндпоинта "/users/<id>/subscribe/".

        Позволяет пользователям подписываться или отписываться
        от обновлений других пользователей.
        """
        author = get_object_or_404(User, id=id)
        if request.method == "POST":
            if request.user == author:
                return Response(
                    {"errors": "Вы не можете подписаться на себя"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                instance = Subscribe.objects.create(
                    subscriber=request.user, author=author
                )
                instance.recipes_count = instance.author.recipes.count
            except IntegrityError:
                return Response(
                    {"errors": "Вы уже подписаны на автора"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = self.get_serializer(instance)
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == "DELETE":
            subscribe = Subscribe.objects.filter(
                subscriber=request.user, author=author
            )
            delete = subscribe.delete()
            if delete[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Вы не были подписаны на автора"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(["GET"], detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request, *args, **kwargs):
        """Функция-обработчик для эндпоинта "/users/subscriptions/".

        Позволяет пользователям просматривать информацию о своих подписках.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.get_object = Subscribe.objects.filter(subscriber=request.user)
        return self.list(request, *args, **kwargs)


class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """Касмомный вьюсет Djoser для создания токена пользователя."""

    serializer_class = TokenCreateSerializer
    permission_classes = [AllowAny]

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = TokenSerializer
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED,
        )


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с тегами.

    Основан на ReadOnlyModelViewSet,
    благодаря чему может быть использован
    только для получения информации о тегах.
    Создание и редактирование тегов доступно
    только через админ-панель.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для работы с ингредиентами.

    Основан на ReadOnlyModelViewSet,
    благодаря чему может быть использован
    только для получения информации об ингредиентах.
    Создание и редактирование ингредиентов доступно
    только через админ-панель.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset


class RecipeViewSet(MultiSerializerViewSetMixin, ModelViewSet):
    """Вьюсет для работы с рецептами.

    Предоставляет пользователям возможность
    создавать/редактировать/удалять свои рецепты,
    получать информацию о чужих рецептах,
    добавлять чужие рецепты в список избранного/список покупок,
    получать информацию о своём списке избранного.
    """

    queryset = Recipe.objects.select_related("author").prefetch_related(
        "tags", "ingredients"
    )
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    ModelViewSet.http_method_names.remove("put")

    serializer_classes = {
        "create": CreateUpdateRecipeSerializer,
        "partial_update": CreateUpdateRecipeSerializer,
        "list": FullRecipeSerializer,
        "retrieve": FullRecipeSerializer,
        "favorite": ShortRecipeSerializer,
        "shopping_cart": ShortRecipeSerializer,
    }

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        is_in_shopping_cart = self.request.query_params.get(
            "is_in_shopping_cart"
        )
        is_favorited = self.request.query_params.get("is_favorited")
        tags = self.request.query_params.getlist("tags")
        author = self.request.query_params.get("author")
        if is_in_shopping_cart:
            queryset = queryset.filter(shoppingcarts__user=user)
        if is_favorited:
            queryset = queryset.filter(favorites__user=user)
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if author:
            queryset = queryset.filter(author=author)
        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(["POST", "DELETE"], detail=False, url_path=r"(?P<id>\w+)/favorite")
    def favorite(self, request, id):
        """Функция-обработчик для эндпоинта "/recipes/<id>/favorite".

        Позволяет пользователям добавлять или
        удалять рецепты из списка избранного.
        """
        user = request.user
        recipe = Recipe.objects.get(id=id)
        if request.method == "POST":
            try:
                Favorite.objects.create(user=user, recipe=recipe)
            except IntegrityError:
                return Response(
                    {"errors": "Рецепт уже в избранном"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = self.get_serializer(recipe)
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == "DELETE":
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            delete = favorite.delete()
            if delete[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Такого рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        ["POST", "DELETE"],
        detail=False,
        url_path=r"(?P<id>\w+)/shopping_cart",
        url_name="shopping_cart",
    )
    def shopping_cart(self, request, id):
        """Функция-обработчик для эндпоинта "/recipes/<id>/shopping_cart".

        Позволяет пользователям добавлять или
        удалять рецепты из списка покупок.
        """
        user = request.user
        recipe = Recipe.objects.get(id=id)
        if request.method == "POST":
            try:
                ShoppingCart.objects.create(user=user, recipe=recipe)
            except IntegrityError:
                return Response(
                    {"errors": "Рецепт уже в списке покупок"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer = self.get_serializer(recipe)
                return Response(
                    data=serializer.data, status=status.HTTP_201_CREATED
                )
        elif request.method == "DELETE":
            shopping_cart = ShoppingCart.objects.filter(
                user=user, recipe=recipe
            )
            delete = shopping_cart.delete()
            if delete[0]:
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Такого рецепта нет в списке покупок"},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(["GET"], detail=False, url_name="download_shopping_cart")
    def download_shopping_cart(self, request):
        """Функция-обработчик для эндпоинта
        "/recipes/<id>/download_shopping_cart".

        Позволяет пользователям получать список покупок в виде TXT файла,
        где все ингредиенты будут суммированы.
        """
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        queryset = ShoppingCart.objects.filter(user=user)

        content = generate_text_of_shopping_cart(user, queryset)
        return HttpResponse(content, content_type="text/plain; charset=utf-8")
