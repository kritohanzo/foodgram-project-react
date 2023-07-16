from django.db import models
from users.models import User

class Ingredient(models.Model):
    name = models.CharField(verbose_name="Название", max_length=64)
    measurement_unit = models.CharField(verbose_name="Единица измерения", max_length=16)

    class Meta:
        verbose_name_plural = "Ингредиенты"
        verbose_name = "Ингредиент"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"], name="unique_name_measurement_unit"
            )
        ]

        
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
    amount = models.IntegerField(verbose_name="Количество")

    class Meta:
        verbose_name_plural = "Связи рецептов и ингредиентов"
        verbose_name = "Связь рецепта и ингредиента"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "ingredient"], name="unique_recipe_ingredient"
            )
        ]

class TagRecipe(models.Model):
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Recipe, on_delete=models.CASCADE, related_name="tags_recipes")
    tag = models.ForeignKey(verbose_name="Тег", to=Tag, on_delete=models.CASCADE, related_name="tags_recipes")

    class Meta:
        verbose_name_plural = "Связи рецептов и тегов"
        verbose_name = "Связь рецепта и тега"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "tag"], name="unique_recipe_tag"
            )
        ]


class Favorite(models.Model):
    user = models.ForeignKey(verbose_name="Пользователь", to=User, on_delete=models.CASCADE, related_name="favorites")
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Recipe, on_delete=models.CASCADE, related_name="favorites")

    class Meta:
        verbose_name_plural = "Списки избранного"
        verbose_name = "Список избранного"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_favorite_user_recipe"
            )
        ]

class ShoppingCart(models.Model):
    user = models.ForeignKey(verbose_name="Пользователь", to=User, on_delete=models.CASCADE, related_name="shoppingcarts")
    recipe = models.ForeignKey(verbose_name="Рецепт", to=Recipe, on_delete=models.CASCADE, related_name="shoppingcarts")

    class Meta:
        verbose_name_plural = "Списки покупок"
        verbose_name = "Список покупок"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shoppingcart_user_recipe"
            )
        ]