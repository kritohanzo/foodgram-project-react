from django.db import models
from users.models import User

class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название", max_length=64, unique=True)
    measurement_unit = models.CharField(verbose_name="Единица измерения", max_length=16)

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"
        ordering = ("name",)
        
    def __str__(self):
        return self.name
    
    

class Tag(models.Model):
    name = models.CharField(verbose_name="Название", max_length=64, unique=True)
    color = models.CharField(verbose_name="Цветовой HEX-код", max_length=7, unique=True)
    slug = models.SlugField(verbose_name="SLUG", max_length=64, unique=True)

    class Meta:
        verbose_name_plural = "Теги"
        verbose_name = "Тег"
        ordering = ("name",)

    def __str__(self):
        return self.name

class Recipe(models.Model):
    author = models.ForeignKey(verbose_name="Автор", to=User, on_delete=models.CASCADE, related_name="recipes")
    name = models.CharField(verbose_name="Название", max_length=128)
    image = models.ImageField(verbose_name="Картинка")
    text = models.TextField(verbose_name="Описание")
    ingredients = models.ManyToManyField(Ingredient, through="IngredientRecipe")
    tags = models.ManyToManyField(Tag, through="TagRecipe")
    cooking_time = models.IntegerField(verbose_name="Время приготовления")
                                       
    class Meta:
        verbose_name_plural = "Рецепты"
        verbose_name = "Рецепт"
        ordering = ("name",)

    def __str__(self):
        return self.name

class IngredientRecipe(models.Model):
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Recipe, on_delete=models.CASCADE, related_name="ingredients_recipes")
    ingredient = models.ForeignKey(verbose_name="Ингредиент", to=Ingredient, on_delete=models.CASCADE, related_name="ingredients_recipes")
    quantity = models.IntegerField(verbose_name="Количество")

class TagRecipe(models.Model):
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Recipe, on_delete=models.CASCADE, related_name="tags_recipes")
    tag = models.ForeignKey(verbose_name="Тег", to=Tag, on_delete=models.CASCADE, related_name="tags_recipes")
