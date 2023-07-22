from django.contrib import admin
from users.models import User, Subscribe

admin.site.site_header = "Администрирование Foodgram"
EMPTY_VALUE_DISPLAY = "—"


class UserConfig(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
    ]
    list_editable = ["username", "email", "first_name", "last_name", "role"]
    search_fields = ["username", "email"]
    empty_value_display = EMPTY_VALUE_DISPLAY


class SubscribeConfig(admin.ModelAdmin):
    list_display = ["id", "subscriber", "author"]
    search_fields = ["subscriber__username", "author__username"]
    empty_value_display = EMPTY_VALUE_DISPLAY


admin.site.register(User, UserConfig)
admin.site.register(Subscribe, SubscribeConfig)
