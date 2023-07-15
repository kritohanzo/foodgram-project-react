from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomDjoserUserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet


router = DefaultRouter()

router.register(r"users", CustomDjoserUserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
]
