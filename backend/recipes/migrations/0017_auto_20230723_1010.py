# Generated by Django 3.2 on 2023-07-23 10:10

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0016_alter_recipe_image"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="recipe",
            options={
                "ordering": ("-pub_date",),
                "verbose_name": "Рецепт",
                "verbose_name_plural": "Рецепты",
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="pub_date",
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name="Дата публикации",
            ),
            preserve_default=False,
        ),
    ]
