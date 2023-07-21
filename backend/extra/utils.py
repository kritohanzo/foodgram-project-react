from django.shortcuts import get_object_or_404
from recipes.models import IngredientRecipe, Ingredient

def create_ingredients(ingredients, recipe):
    """Вспомогательная функция для добавления ингредиентов.
    Используется при создании/редактировании рецепта."""
    ingredients_list = []
    for ingredient in ingredients:
        current_ingredient = get_object_or_404(Ingredient,
                                               id=ingredient.get('id'))
        amount = ingredient.get('amount')
        ingredients_list.append(
            IngredientRecipe(
                recipe=recipe,
                ingredient=current_ingredient,
                amount=amount
            )
        )
    IngredientRecipe.objects.bulk_create(ingredients_list)

def generate_txt(user, shopping_cart_queryset):
    shopping_cart = dict()
    for row_of_shopping_cart in shopping_cart_queryset:
        rows_of_recipe_ingredients = IngredientRecipe.objects.filter(recipe=row_of_shopping_cart.recipe)
        for row_of_recipe_ingredient in rows_of_recipe_ingredients:
            ingredient = Ingredient.objects.get(id=row_of_recipe_ingredient.ingredient.id)
            name = ingredient.name.capitalize() + f" ({ingredient.measurement_unit})"
            value = row_of_recipe_ingredient.amount
            if ingredient.name in shopping_cart:
                shopping_cart[name] += value
            else:
                shopping_cart[name] = value

    header = f" {user.get_full_name()}, спасибо, что пользуетесь нашим сервисом.\nСпециально для вас мы подготовили список ингредиентов для вашего списка покупок:\n\n"  
    footer = "\n\nВаш персональный помощник — Foodgram!"          
    content = header + "\n".join([f"{igredient_name} — {amount_measurement_unit}" for igredient_name, amount_measurement_unit in shopping_cart.items()]) + footer
    return content