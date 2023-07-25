from django.contrib import admin

from core.filters import AuthorFilter, NameFilter, TagsFilter
from recipes.models import (Favorite, Ingredient, IngredientRecipe, Recipe,
                            Tag, TagRecipe,)


admin.site.site_header = "Администрирование Foodgram"
EMPTY_VALUE_DISPLAY = "—"


@admin.register(Tag)
class TagConfig(admin.ModelAdmin):
    list_display = ["id", "name", "color", "slug"]
    list_display_links = ["id", "name"]
    search_fields = ["name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Ingredient)
class IngredientConfig(admin.ModelAdmin):
    list_display = ["id", "name", "measurement_unit"]
    list_display_links = ["id", "name"]
    search_fields = ["name"]
    empty_value_display = EMPTY_VALUE_DISPLAY


class IngredientRecipeInline(admin.TabularInline):
    model = IngredientRecipe


@admin.register(Recipe)
class RecipeConfig(admin.ModelAdmin):
    inlines = [IngredientRecipeInline]
    list_display = [
        "id",
        "author",
        "name",
        "text",
    ]
    list_display_links = ["id", "name"]
    readonly_fields = ["pub_date", "count_favorites"]
    search_fields = [
        "name",
        "author__username",
        "tags__name",
        "ingredients__name",
    ]
    list_filter = [NameFilter, AuthorFilter]

    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_queryset(self, request):
        queryset = (
            super(RecipeConfig, self)
            .get_queryset(request)
            .select_related("author")
            .prefetch_related("ingredients", "tags")
        )
        return queryset

    def get_ingredients(self, obj):
        return [ingredient.name for ingredient in obj.ingredients.all()]

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def count_favorites(self, obj):
        return obj.favorites.count()

    get_tags.short_description = "Теги"
    get_ingredients.short_description = "Ингредиенты"
    count_favorites.short_description = "В избранном"


@admin.register(TagRecipe)
class TagRecipeConfig(admin.ModelAdmin):
    list_display = ["id", "tag", "recipe"]
    search_fields = ["tag__name", "recipe__name"]
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_queryset(self, request):
        queryset = (
            super(TagRecipeConfig, self)
            .get_queryset(request)
            .select_related("tag", "recipe")
        )
        return queryset


@admin.register(IngredientRecipe)
class IngredientRecipeConfig(admin.ModelAdmin):
    list_display = ["id", "ingredient", "recipe"]
    search_fields = ["ingredient__name", "recipe__name"]
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_queryset(self, request):
        queryset = (
            super(IngredientRecipeConfig, self)
            .get_queryset(request)
            .select_related("ingredient", "recipe")
        )
        return queryset


@admin.register(Favorite)
class FavoriteConfig(admin.ModelAdmin):
    list_display = ["id", "user", "recipe"]
    search_fields = ["user__username", "recipe__name"]
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_queryset(self, request):
        queryset = (
            super(FavoriteConfig, self)
            .get_queryset(request)
            .select_related("user", "recipe")
        )
        return queryset
