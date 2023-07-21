from rest_framework.serializers import ModelSerializer, ImageField
from rest_framework import serializers
from recipes.models import Ingredient, Tag, Recipe, IngredientRecipe, ShoppingCart, Favorite
from rest_framework.exceptions import ValidationError
from users.models import User, Subscribe
from django.core.files.base import ContentFile
import base64
from extra.utils import create_ingredients

class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "email", "username", "first_name", "last_name", "is_subscribed")
        read_only_fields = ("email",)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Subscribe.objects.filter(subscriber=request.user.id, author=obj).exists())


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")
        read_only_fields = ("name", "measurement_unit")


class IngredientRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.CharField(source="ingredient.name")
    measurement_unit = serializers.CharField(source="ingredient.measurement_unit")
    class Meta:
        model = IngredientRecipe
        fields = ('id', 'name', 'measurement_unit', 'amount')

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
    
class CreateIngredientRecipeSerialiez(serializers.ModelSerializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    
    class Meta:
        model = IngredientRecipe
        fields = ("id", "amount")

class ShortRecipeSerializer(ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")

class FullRecipeSerializer(ModelSerializer):
    image = Base64ToImageField()
    author = UserSerializer(required=False)
    tags = TagSerializer(many=True)
    ingredients = IngredientRecipeSerializer(many=True, read_only=True, source='ingredients_recipes')
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Recipe
        fields = ("id", "tags", "author", "ingredients", "name", "image", "text", "cooking_time", "is_in_shopping_cart", "is_favorited")
        read_only_fields = ('author',)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and ShoppingCart.objects.filter(user=request.user, recipe=obj).exists())

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request.user.is_authenticated and Favorite.objects.filter(user=request.user, recipe=obj).exists())

class CreateUpdateRecipeSerializer(ModelSerializer):
    image = Base64ToImageField()
    ingredients = CreateIngredientRecipeSerialiez(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )

    class Meta:
        model = Recipe
        fields = ("id", "tags", "ingredients", "name", "image", "text", "cooking_time")

    def validate_ingredients(self, value):
        ingredients_list = []
        for ingredient in value:
            if ingredient.get('amount') <= 0:
                raise serializers.ValidationError(
                    'Количество не может быть меньше 1'
                )
            ingredients_list.append(ingredient.get('id'))
        if len(set(ingredients_list)) != len(ingredients_list):
            raise serializers.ValidationError(
                'Вы пытаетесь добавить в рецепт два одинаковых ингредиента'
            )
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        create_ingredients(ingredients, recipe)
        return recipe
    

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.remove()
        instance.tags.set(tags)
        IngredientRecipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        create_ingredients(ingredients, instance)
        return instance
    
    def to_representation(self, instance):
        request = self.context.get('request')
        return FullRecipeSerializer(
            instance,
            context={'request': request}
        ).data

        

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
        request = self.context.get('request')
        return (request and
                request.user and
                Subscribe.objects.filter(subscriber=obj.subscriber, author=obj.author).exists()
        )

    def get_recipes(self, obj):
        return ShortRecipeSerializer(Recipe.objects.filter(author=obj.author), many=True).data
    
    def get_recipes_count(self, obj):
        return len(self.get_recipes(obj))
