from rest_framework.viewsets import ModelViewSet, GenericViewSet
from users.models import User, Subscribe
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny, IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from api.permissions import IsAuthorOrReadOnly
from django.contrib.auth import update_session_auth_hash
from recipes.models import Ingredient, Tag, Recipe, Favorite, ShoppingCart, IngredientRecipe
from django.shortcuts import get_object_or_404
from api.serializers import IngredientSerializer, TagSerializer, FullRecipeSerializer, ShortRecipeSerializer, CreateUpdateRecipeSerializer, SubscribeSerializer, UserSerializer
from rest_framework.viewsets import mixins
from rest_framework.exceptions import NotAuthenticated
from djoser.serializers import UserCreateSerializer, SetPasswordSerializer, TokenCreateSerializer, TokenSerializer
from rest_framework.views import APIView
from djoser import utils
from djoser.compat import get_user_email
from djoser.conf import settings
from django.shortcuts import HttpResponse
from extra.utils import generate_txt

class UserViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.CreateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == "subscribe" or self.action == "subscriptions":
            return Subscribe.objects.filter(subscriber=self.request.user)
        return super().get_queryset()

    def get_permissions(self):
        if self.action == "create" or self.action == "list":
            self.permission_classes = [AllowAny]
        elif self.action == "set_password" or self.action == "me" or self.action == "subscribe" or self.action == "subscriptions":
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "set_password":
            return SetPasswordSerializer
        elif self.action == "subscribe" or self.action == "subscriptions":
            return SubscribeSerializer
        return super().get_serializer_class()

    def get_instance(self):
        return self.request.user

    @action(["get"], detail=False)
    def me(self, request, *args, **kwargs):
        self.get_object = self.get_instance
        return self.retrieve(request, *args, **kwargs)
        
    @action(["post"], detail=False, url_name='set_password')
    def set_password(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(serializer.data["new_password"])
        self.request.user.save()
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

class TokenCreateView(utils.ActionViewMixin, generics.GenericAPIView):
    """Use this endpoint to obtain user authentication token."""

    serializer_class = TokenCreateSerializer
    permission_classes = [AllowAny]

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = TokenSerializer
        return Response(
            data=token_serializer_class(token).data, status=status.HTTP_201_CREATED
        )

class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = self.queryset
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        return queryset

class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = ShortRecipeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    ModelViewSet.http_method_names.remove('put')

    def get_serializer_class(self):
        if self.action == "create" or self.action == "partial_update":
            return CreateUpdateRecipeSerializer
        elif self.action == "list" or self.action == "retrieve":
            return FullRecipeSerializer
        return self.serializer_class

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        is_in_shopping_cart = self.request.query_params.get('is_in_shopping_cart')
        is_favorited = self.request.query_params.get('is_favorited')
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
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
        user = request.user
        recipe = Recipe.objects.get(id=id)
        if request.method == "POST":
            try:
                Favorite.objects.create(user=user, recipe=recipe)
            except:
                return Response({"errors": "Рецепт уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = self.get_serializer(recipe)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"errors": "Такого рецепта нет в избранном"}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(["POST", "DELETE"], detail=False, url_path=r"(?P<id>\w+)/shopping_cart", url_name="shopping_cart")
    def shopping_cart(self, request, id):
        user = request.user
        recipe = Recipe.objects.get(id=id)
        if request.method == "POST":
            try:
                ShoppingCart.objects.create(user=user, recipe=recipe)
            except:
                return Response({"errors": "Рецепт уже в списке покупок"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = self.get_serializer(recipe)
                return Response(data=serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            shopping_cart = ShoppingCart.objects.filter(user=user, recipe=recipe)
            if shopping_cart.exists():
                shopping_cart.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"errors": "Такого рецепта нет в списке покупок"}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(["GET"], detail=False, url_name='download_shopping_cart')
    def download_shopping_cart(self, request): 
        user = request.user
        if not user.is_authenticated:
            raise NotAuthenticated
        queryset = ShoppingCart.objects.filter(user=user)
        
        content = generate_txt(user, queryset)
        return HttpResponse(content, content_type='text/plain; charset=utf-8')   