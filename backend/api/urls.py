from djoser.views import TokenDestroyView
from rest_framework.routers import DefaultRouter

from django.urls import include, path
from django.views.generic import TemplateView

from api.views import TokenCreateView

from .views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet


app_name = "api"

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", TokenCreateView.as_view(), name="token_login"),
    path(
        "auth/token/logout/", TokenDestroyView.as_view(), name="token_logout"
    ),
    path("docs/", TemplateView.as_view(template_name="redoc.html")),
    path(
        "docs/openapi-schema.yml/",
        TemplateView.as_view(template_name="openapi-schema.yml"),
    ),
]
