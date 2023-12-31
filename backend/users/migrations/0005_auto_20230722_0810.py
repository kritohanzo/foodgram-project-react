# Generated by Django 3.2 on 2023-07-22 08:10

import core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0004_auto_20230704_1626"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="subscribe",
            options={
                "ordering": ("id",),
                "verbose_name": "Подписка пользователя",
                "verbose_name_plural": "Подписки пользователей",
            },
        ),
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(
                max_length=150,
                unique=True,
                validators=[core.validators.validate_username],
                verbose_name="Логин",
            ),
        ),
    ]
