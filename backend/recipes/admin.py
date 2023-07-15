from django.contrib import admin
from recipes.models import Tag, Ingredient

class TagConfig(admin.ModelAdmin):
    list_display = ["id", "name", "color", "slug"]
    list_editable = ["name", "color", "slug"]
    search_fields = ["name"]
    empty_value_display = "<нет>"

class IngredientConfig(admin.ModelAdmin):
    list_display = ["id", "name", "measurement_unit"]
    list_editable = ["name", "measurement_unit"]
    search_fields = ["name"]
    empty_value_display = "<нет>"

admin.site.register(Tag, TagConfig)
admin.site.register(Ingredient, IngredientConfig)