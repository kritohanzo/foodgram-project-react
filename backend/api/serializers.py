import base64

from rest_framework import serializers
from rest_framework.serializers import ImageField, ModelSerializer

from django.core.files.base import ContentFile

from core.utils import create_ingredients
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            ShoppingCart, Tag,)
from users.models import Subscribe, User


class Base64ToImageField(ImageField):
    """Вспомогательный класс для работы с изображениями."""

    def to_internal_value(self, data):
        format, img = data.split(";base64,")
        ext = format.split("/")[-1]
        data = ContentFile(base64.b64decode(img), name="temp." + ext)
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор, использующийся для вывода информации о пользователе."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and Subscribe.objects.filter(
                subscriber=request.user.id, author=obj
            ).exists()
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор, использующийся для вывода
    информации об ингредиентах вне рецепта.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор, использующийся для вывода
    информации об ингредиентах в рецепте.
    """

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit"
    )

    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit", "amount")


class TagSerializer(ModelSerializer):
    """Сериализатор, использующийся для вывода информации об тегах."""

    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")


class CreateIngredientRecipeSerialiez(serializers.ModelSerializer):
    """
    Сериализатор, испольщующийся для преобразования поступающей информации
    об ингредиентах при создании нового рецепта.
    """

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")


class ShortRecipeSerializer(ModelSerializer):
    """
    Сериализатор, использующийся для вывода
    информации о рецепте в коротком виде.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class FullRecipeSerializer(ModelSerializer):
    """
    Сериализатор, использующийся для вывода
    информации о рецепте в полном виде.
    """

    image = Base64ToImageField()
    author = UserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(
        many=True, source="ingredients_recipes"
    )
    is_in_shopping_cart = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
            "is_in_shopping_cart",
            "is_favorited",
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and ShoppingCart.objects.filter(
                user=request.user, recipe=obj
            ).exists()
        )

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        return (
            request.user.is_authenticated
            and Favorite.objects.filter(user=request.user, recipe=obj).exists()
        )


class CreateUpdateRecipeSerializer(ModelSerializer):
    """Сериализатор, использующийся при создании нового рецепта."""

    image = Base64ToImageField()
    ingredients = CreateIngredientRecipeSerialiez(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "ingredients",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                "Вы не добавили ни одного ингредиента."
            )
        ingredients_list = [ingredient.get("id") for ingredient in value]
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                "Вы пытаетесь добавить в рецепт два одинаковых ингредиента."
            )
        return value

    def validate_tags(self, value):
        if not value:
            raise serializers.ValidationError("Вы не добавили ни одного тега.")
        if len(set(value)) != len(value):
            raise serializers.ValidationError(
                "Вы пытаетесь добавить в рецепт два одинаковых тега."
            )
        return value

    def create(self, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        try:
            create_ingredients(ingredients, recipe)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                {"ingredients": "Такой ингредиент не существует."}
            )
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags")
        ingredients = validated_data.pop("ingredients")
        instance.tags.remove()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        try:
            create_ingredients(ingredients, instance)
        except Ingredient.DoesNotExist:
            raise serializers.ValidationError(
                {"ingredients": "Такой ингредиент не существует."}
            )
        return instance

    def to_representation(self, instance):
        request = self.context.get("request")
        return FullRecipeSerializer(
            instance, context={"request": request}
        ).data


class SubscribeSerializer(ModelSerializer):
    """Сериализатор, использующийся при работе с подписками пользователей."""

    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (
            request
            and request.user
            and Subscribe.objects.filter(
                subscriber=obj.subscriber, author=obj.author
            ).exists()
        )

    def get_recipes(self, obj):
        return ShortRecipeSerializer(
            Recipe.objects.filter(author=obj.author), many=True
        ).data
