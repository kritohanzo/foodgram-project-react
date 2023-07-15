from rest_framework.serializers import ModelSerializer, ImageField
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe, TagRecipe, IngredientRecipe
from rest_framework.exceptions import ValidationError
from users.models import User, Subscribe
from django.core.files.base import ContentFile
import base64
from django.shortcuts import get_object_or_404
import djoser.serializers

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
    
class RecipeSerializer(ModelSerializer):
    #is_favorited = serializers.SerializerMethodField()
    image = Base64ToImageField()
    author = djoser.serializers.UserSerializer()
    class Meta:
        model = Recipe
        #fields = ("id", "tags", "author", "ingredients", "is_favorited", "is_in_shopping_cart", "name", "image", "text", "cooking_time")
        fields = ("id", "tags", "author", "ingredients", "name", "image", "text", "cooking_time")
        read_only_fields = ('author',)

    #def get_is_favorited(self, obj):


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

    def get_is_subscribed(self, obj):
        return Subscribe.objects.filter(subscriber=obj.subscriber, author=obj.author).exists()
    
    def get_recipes(self, obj):
        return Recipe.objects.filter(author=obj.author)
    
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
