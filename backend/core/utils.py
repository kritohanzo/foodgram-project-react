import base64

from rest_framework.serializers import ImageField, ValidationError

from django.core.files.base import ContentFile
from django.db.models import QuerySet

from recipes.models import Ingredient, IngredientRecipe, Recipe
from users.models import User


class Base64ToImageField(ImageField):
    """Вспомогательный класс для работы с изображениями."""

    def to_internal_value(self, data):
        format, img = data.split(";base64,")
        ext = format.split("/")[-1]
        data = ContentFile(base64.b64decode(img), name="temp." + ext)
        return super().to_internal_value(data)


def create_ingredients(ingredients: list[dict[int]], recipe: Recipe) -> None:
    """
    Вспомогательная функция для добавления ингредиентов, которая
    используется при создании/редактировании рецепта.
    """
    ingredients_list = []
    for ingredient in ingredients:
        try:
            current_ingredient = Ingredient.objects.get(
                id=ingredient.get("id")
            )
        except Ingredient.DoesNotExist:
            raise ValidationError(
                {"ingredients": "Такой ингредиент не существует."}
            )
        amount = ingredient.get("amount")
        ingredients_list.append(
            IngredientRecipe(
                recipe=recipe, ingredient=current_ingredient, amount=amount
            )
        )
    IngredientRecipe.objects.bulk_create(ingredients_list)


def generate_txt(user: User, shopping_cart_queryset: QuerySet) -> str:
    """Вспомогательная функция для генерации TXT файла."""
    shopping_cart = dict()
    for row_of_shopping_cart in shopping_cart_queryset:
        rows_of_recipe_ingredients = IngredientRecipe.objects.filter(
            recipe=row_of_shopping_cart.recipe
        )
        for row_of_recipe_ingredient in rows_of_recipe_ingredients:
            ingredient = Ingredient.objects.get(
                id=row_of_recipe_ingredient.ingredient.id
            )
            name = (
                ingredient.name.capitalize()
                + f" ({ingredient.measurement_unit})"
            )
            value = row_of_recipe_ingredient.amount
            if ingredient.name in shopping_cart:
                shopping_cart[name] += value
            else:
                shopping_cart[name] = value
    header = (
        f"{user.get_full_name()}, спасибо, что пользуетесь нашим сервисом.\n"
        "Специально для вас мы подготовили список ингредиентов"
        "для вашего списка покупок:\n\n"
    )
    footer = "\n\nВаш персональный помощник — Foodgram!"
    content = (
        header
        + "\n".join(
            [
                f"{igredient_name} — {amount_measurement_unit}"
                for igredient_name, amount_measurement_unit
                in shopping_cart.items()
            ]
        )
        + footer
    )
    return content
