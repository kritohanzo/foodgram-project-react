from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomDjoserUserViewSet, TagViewSet, IngredientViewSet, RecipeViewSet
from django.views.generic import TemplateView
from djoser.views import TokenDestroyView
from api.views import CustomDjoserTokenCreateView

app_name = 'api'

router = DefaultRouter()

router.register(r"users", CustomDjoserUserViewSet, basename="users")
router.register(r"tags", TagViewSet, basename="tags")
router.register(r"ingredients", IngredientViewSet, basename="ingredients")
router.register(r"recipes", RecipeViewSet, basename="recipes")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/token/login/", CustomDjoserTokenCreateView.as_view(), name='token_login'),
    path("auth/token/logout/", TokenDestroyView.as_view()),
    path('docs/', TemplateView.as_view(template_name="redoc.html")),
    path('docs/openapi-schema.yml/', TemplateView.as_view(template_name="openapi-schema.yml")),
]
