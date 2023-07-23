from django.contrib import admin

from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Tag, TagRecipe,)


admin.site.site_header = "Администрирование Foodgram"
EMPTY_VALUE_DISPLAY = "—"


class TagConfig(admin.ModelAdmin):
    list_display = ["id", "name", "color", "slug"]
    list_editable = ["name", "color", "slug"]
    search_fields = ["name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientConfig(admin.ModelAdmin):
    list_display = ["id", "name", "measurement_unit"]
    list_editable = ["name", "measurement_unit"]
    search_fields = ["name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


class RecipeConfig(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]
    list_display = [
        "id",
        "author",
        "name",
        "text",
    ]
    readonly_fields = ["count_favorites"]
    list_editable = ["name", "text"]
    search_fields = [
        "name",
        "author__username",
        "tags__name",
        "ingredients__name",
    ]
    list_filter = ["name", "author", "tags"]
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_ingredients(self, obj):
        return [ingredient.name for ingredient in obj.ingredients.all()]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def count_favorites(self, obj):
        return obj.favorites.count()

    get_tags.short_description = "Теги"
    get_ingredients.short_description = "Ингредиенты"
    count_favorites.short_description = "В избранном"


class TagRecipeConfig(admin.ModelAdmin):
    list_display = ["id", "tag", "recipe"]
    search_fields = ["tag__name", "recipe__name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientRecipeConfig(admin.ModelAdmin):
    list_display = ["id", "ingredient", "recipe"]
    search_fields = ["ingredient__name", "recipe__name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


class FavoriteConfig(admin.ModelAdmin):
    list_display = ["id", "user", "recipe"]
    search_fields = ["user__username", "recipe__name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(Tag, TagConfig)
admin.site.register(Ingredient, IngredientConfig)
admin.site.register(Recipe, RecipeConfig)
admin.site.register(TagRecipe, TagRecipeConfig)
admin.site.register(IngredientRecipe, IngredientRecipeConfig)
admin.site.register(Favorite, FavoriteConfig)
