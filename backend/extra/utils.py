from django.shortcuts import get_object_or_404
from recipes.models import IngredientRecipe, Ingredient

def create_ingredients(ingredients, recipe):
    """Вспомогательная функция для добавления ингредиентов.
    Используется при создании/редактировании рецепта."""
    ingredients_list = []
    print(ingredients)
    for ingredient in ingredients:
        #print(ingredient)
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
        #print(ingredients_list)
    IngredientRecipe.objects.bulk_create(ingredients_list)