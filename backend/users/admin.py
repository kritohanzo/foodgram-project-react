from django.contrib import admin

from users.models import Subscribe, User


admin.site.site_header = "Администрирование Foodgram"
EMPTY_VALUE_DISPLAY = "—"


@admin.register(User)
class UserConfig(admin.ModelAdmin):
    list_display = [
        "id",
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
    ]
    list_editable = [
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
    ]
    search_fields = ["username", "email"]
    empty_value_display = EMPTY_VALUE_DISPLAY


@admin.register(Subscribe)
class SubscribeConfig(admin.ModelAdmin):
    list_display = ["id", "subscriber", "author"]
    search_fields = ["subscriber__username", "author__username"]
    empty_value_display = EMPTY_VALUE_DISPLAY

    def get_queryset(self, request):
        queryset = Subscribe.objects.select_related('author', 'subscriber')
        return queryset
