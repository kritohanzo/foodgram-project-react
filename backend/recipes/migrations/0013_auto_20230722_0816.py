# Generated by Django 3.2 on 2023-07-22 08:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0012_auto_20230722_0810"),
    ]

    operations = [
        migrations.AlterField(
            model_name="ingredientrecipe",
            name="amount",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Количество должно быть больше 0"
                    )
                ],
                verbose_name="Количество",
            ),
        ),
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.IntegerField(
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Время приготовления должно быть больше 0"
                    )
                ],
                verbose_name="Время приготовления",
            ),
        ),
    ]
