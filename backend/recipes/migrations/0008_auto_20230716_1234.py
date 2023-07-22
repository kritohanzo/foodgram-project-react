# Generated by Django 3.2 on 2023-07-16 12:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("recipes", "0007_rename_quantity_ingredientrecipe_amount"),
    ]

    operations = [
        migrations.CreateModel(
            name="FavoriteRecipe",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Список избранного",
                "verbose_name_plural": "Списки избранного",
                "ordering": ("id",),
            },
        ),
        migrations.AlterModelOptions(
            name="ingredientrecipe",
            options={
                "ordering": ("id",),
                "verbose_name": "Связь рецепта и ингредиента",
                "verbose_name_plural": "Связи рецептов и ингредиентов",
            },
        ),
        migrations.AlterModelOptions(
            name="tagrecipe",
            options={
                "ordering": ("id",),
                "verbose_name": "Связь рецепта и тега",
                "verbose_name_plural": "Связи рецептов и тегов",
            },
        ),
        migrations.AddConstraint(
            model_name="ingredientrecipe",
            constraint=models.UniqueConstraint(
                fields=("recipe", "ingredient"),
                name="unique_recipe_ingredient",
            ),
        ),
        migrations.AddConstraint(
            model_name="tagrecipe",
            constraint=models.UniqueConstraint(
                fields=("recipe", "tag"), name="unique_recipe_tag"
            ),
        ),
        migrations.AddField(
            model_name="favoriterecipe",
            name="recipe",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to="recipes.recipe",
                verbose_name="Рецепт",
            ),
        ),
        migrations.AddField(
            model_name="favoriterecipe",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="favorites",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Пользователь",
            ),
        ),
        migrations.AddConstraint(
            model_name="favoriterecipe",
            constraint=models.UniqueConstraint(
                fields=("user", "recipe"), name="unique_user_recipe"
            ),
        ),
    ]
