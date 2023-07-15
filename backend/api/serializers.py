from rest_framework.serializers import ModelSerializer, ImageField
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe, TagRecipe, IngredientRecipe
from rest_framework.exceptions import ValidationError
from users.models import User, Subscribe
from django.core.files.base import ContentFile
import base64
from django.shortcuts import get_object_or_404
import djoser.serializers
import json
from djoser import utils
from djoser.compat import get_user_email, get_user_email_field_name
from djoser.conf import settings

class CustomDjoserUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            settings.USER_ID_FIELD,
            settings.LOGIN_FIELD,
            "is_subscribed"
        )
        read_only_fields = (settings.LOGIN_FIELD,)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return Subscribe.objects.filter(subscriber=request.user.id, author=obj).exists()


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = IngredientRecipe
        fields = ("id", "name", "measurement_unit")

class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")

class Base64ToImageField(ImageField):
    def to_internal_value(self, data):
        format, img = data.split(';base64,')
        ext = format.split('/')[-1]
        data = ContentFile(base64.b64decode(img), name='temp.' + ext)
        return super().to_internal_value(data)
    
class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

class FullRecipeSerializer(ModelSerializer):
    image = Base64ToImageField()
    author = CustomDjoserUserSerializer(required=False)
    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients", "name", "image", "text", "cooking_time")
        read_only_fields = ('author',)

class CreateUpdateRecipeSerializer(ModelSerializer):
    image = Base64ToImageField()
    ingredients = IngredientSerializer(many=True)
    tags = TagSerializer(many=True)
    class Meta:
        model = Recipe
        fields = ("id", "tags", "ingredients", "name", "image", "text", "cooking_time")

class SubscribeSerializer(ModelSerializer):
    email = serializers.ReadOnlyField(source="author.email")
    id = serializers.ReadOnlyField(source="author.id")
    username = serializers.ReadOnlyField(source="author.username")
    first_name = serializers.ReadOnlyField(source="author.first_name")
    last_name = serializers.ReadOnlyField(source="author.last_name")
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = Subscribe
        fields = ("id", "username", "email", "first_name", "last_name", "is_subscribed", "recipes", "recipes_count")
        #read_only_fields = ("recipes",)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request and
                request.user and
                Subscribe.objects.filter(subscriber=obj.subscriber, author=obj.author).exists()
        )

    def get_recipes(self, obj):
        return ShortRecipeSerializer(Recipe.objects.filter(author=obj.author), many=True).data
    
    def get_recipes_count(self, obj):
        return len(self.get_recipes(obj))
    
class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "color", "slug")
