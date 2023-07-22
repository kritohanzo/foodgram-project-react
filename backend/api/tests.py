from rest_framework.test import APITestCase
from users.models import User, Subscribe
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from recipes.models import Tag, Ingredient, Recipe, Favorite, ShoppingCart
from rest_framework.test import APIClient
from rest_framework.test import override_settings
import shutil
import tempfile
from copy import deepcopy
from core.utils import create_ingredients

MEDIA_ROOT = tempfile.mkdtemp()


class CreateUserTest(APITestCase):
    def test_can_create_user(self):
        """
        Проверяем, что пользователь может зарегистрироваться.
        """
        request_data = {
            "email": "test@mail.ru",
            "username": "test",
            "first_name": "Test",
            "last_name": "Testov",
            "password": "mysecretpassword",
        }
        response = self.client.post(reverse("api:users-list"), request_data)
        expected_data = {
            "email": "test@mail.ru",
            "username": "test",
            "first_name": "Test",
            "last_name": "Testov",
            "id": 1,
        }
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Запрос возвращает не 201 код",
        )
        self.assertEqual(
            User.objects.all().count(),
            1,
            "Пользователь не создается в базе данных",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )


class CreataTokenTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@mail.ru", username="test")
        self.user_password = "mysecretpassword"
        self.user.set_password(self.user_password)
        self.user.save()
        self.token_count = Token.objects.all().count()

    def test_can_get_token(self):
        """
        Проверяем, что зарегистрированный пользователь может получить токен.
        """
        request_data = {
            "email": self.user.email,
            "password": self.user_password,
        }
        response = self.client.post(reverse("api:token_login"), request_data)
        token_count = Token.objects.all().count()
        expected_data = {"auth_token": Token.objects.get(user=self.user).key}
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Ответ API содержит не 201 код",
        )
        self.assertEqual(
            token_count,
            self.token_count + 1,
            "Токен не создается в базе данных",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )


class DestroyTokenTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="test@mail.ru", username="test")
        self.user.set_password("mysecretpassword")
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token_count = Token.objects.all().count()
        self.client = APIClient()

    def test_auth_can_destroy_token(self):
        """
        Проверяем, что аутентифицированный пользователь
        может уничтожить свой токен.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(reverse("api:token_logout"))
        token_count = Token.objects.all().count()
        expected_data = None
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Ответ API содержит не 204 код",
        )
        self.assertEqual(
            token_count,
            self.token_count - 1,
            "Токен не удаляется из базы данных",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauth_cant_destroy_token(self):
        """
        Проверяем, что неаутентифицированный
        пользователь не может уничтожить токен.
        """
        response = self.client.post(reverse("api:token_logout"))
        token_count = Token.objects.all().count()
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Ответ API содержит не 401 код",
        )
        self.assertEqual(
            token_count,
            self.token_count,
            "Токен всё равно удалился из базы данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class ListUsersTest(APITestCase):
    def setUp(self):
        self.user_1 = User.objects.create(
            username="test1",
            email="test1@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.user_2 = User.objects.create(
            username="test2",
            email="test2@mail.ru",
            first_name="Test",
            last_name="Testov",
        )

    def test_can_list_users(self):
        """
        Проверяем, что любой пользователь
        может получить информацию о других пользователях.
        """
        response = self.client.get(reverse("api:users-list"))
        expected_data = [
            {
                "email": self.user_1.email,
                "username": self.user_1.username,
                "first_name": self.user_1.first_name,
                "last_name": self.user_1.last_name,
                "id": self.user_1.id,
                "is_subscribed": False,
            },
            {
                "email": self.user_2.email,
                "username": self.user_2.username,
                "first_name": self.user_2.first_name,
                "last_name": self.user_2.last_name,
                "id": self.user_2.id,
                "is_subscribed": False,
            },
        ]
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data.get("results"),
            expected_data,
            "Тело ответа API не соответствует документации",
        )


class RetrieveUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_auth_can_retrieve_user(self):
        """
        Проверяем, что аутентифицированный пользователь
        может получить информацию о другим пользователе.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            reverse("api:users-detail", args=[self.user.id])
        )
        expected_data = {
            "email": self.user.email,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "id": self.user.id,
            "is_subscribed": False,
        }
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_cant_retrieve_nonexistent_user(self):
        """
        Проверяем, что пользователь не может
        получить информацию о несуществующем пользователе.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            reverse("api:users-detail", args=[self.user.id + 1])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"detail": "Страница не найдена."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauth_cant_retrieve_user(self):
        """
        Проверяем, что неаутентифицированный пользователь
        не может получить информацию о другим пользователе.
        """
        response = self.client.get(
            reverse("api:users-detail", args=[self.user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class CurrentUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_auth_can_get_current_user(self):
        """
        Проверяем, что аутентифицированный пользователь
        может получить информацию о себе.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(reverse("api:users-me"))
        expected_data = {
            "email": self.user.email,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "id": self.user.id,
            "is_subscribed": False,
        }
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauth_cant_get_current_user(self):
        """
        Проверяем, что неаутентифицированный пользователь
        не может получить информацию о себе.
        """
        response = self.client.get(reverse("api:users-me"))
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class SetPasswordUserTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.user.set_password("mysecretpassword")
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.client = APIClient()

    def test_auth_can_set_password(self):
        """
        Проверяем, что аутентифицированный пользователь
        может сменить свой пароль.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        request_data = {
            "new_password": "newsecretpassword",
            "current_password": "mysecretpassword",
        }
        response = self.client.post(
            reverse("api:users-set_password"), request_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Корректный запрос возвращает не 204 код",
        )
        response = self.client.post(
            reverse("api:users-set_password"), request_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Некорректный запрос возвращает не 400 код",
        )
        self.assertIn(
            "current_password",
            response.data,
            "Тело ответа API не соответствует документации",
        )
        self.assertEqual(
            response.data,
            {"current_password": ["Неправильный пароль."]},
            "Пароль пользователя не меняется",
        )

    def test_noauth_cant_set_password(self):
        """
        Проверяем, что неаутентифицированный пользователь
        не может сменить свой пароль.
        """
        request_data = {
            "new_password": "newsecretpassword",
            "current_password": "mysecretpassword",
        }
        response = self.client.post(
            reverse("api:users-set_password"), request_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class ListTagsTest(APITestCase):
    def setUp(self):
        self.tag_1 = Tag.objects.create(
            name="tag1", color="#111111", slug="tag1"
        )
        self.tag_2 = Tag.objects.create(
            name="tag2", color="#222222", slug="tag2"
        )

    def test_cat_list_tags(self):
        """
        Проверяем, что любой пользователь может получить список тегов.
        """
        expected_data = [
            {
                "id": self.tag_1.id,
                "name": self.tag_1.name,
                "color": self.tag_1.color,
                "slug": self.tag_1.slug,
            },
            {
                "id": self.tag_2.id,
                "name": self.tag_2.name,
                "color": self.tag_2.color,
                "slug": self.tag_2.slug,
            },
        ]
        response = self.client.get(reverse("api:tags-list"))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )


class RetrieveTagTest(APITestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="tag", color="#111111", slug="tag")

    def test_can_retrieve_tag(self):
        """
        Проверяем, что любой пользователь может получить конкретный тег.
        """
        expected_data = {
            "id": self.tag.id,
            "name": self.tag.name,
            "color": self.tag.color,
            "slug": self.tag.slug,
        }
        response = self.client.get(
            reverse("api:tags-detail", args=[self.tag.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_cant_retrive_nonexistent_tag(self):
        """
        Проверяем, что любой пользователь не может
        получить несуществующий конкретный тег.
        """
        response = self.client.get(
            reverse("api:tags-detail", args=[self.tag.id + 1])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"detail": "Страница не найдена."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class ListIngredientsTest(APITestCase):
    def setUp(self):
        self.ingredient_1 = Ingredient.objects.create(
            name="milk", measurement_unit="г"
        )
        self.ingredient_2 = Ingredient.objects.create(
            name="cucumber", measurement_unit="г"
        )

    def test_cat_list_ingredients(self):
        """
        Проверяем, что любой пользователь может получить список ингредиентов.
        """
        expected_data = [
            {
                "id": self.ingredient_2.id,
                "name": self.ingredient_2.name,
                "measurement_unit": self.ingredient_2.measurement_unit,
            },
            {
                "id": self.ingredient_1.id,
                "name": self.ingredient_1.name,
                "measurement_unit": self.ingredient_1.measurement_unit,
            },
        ]
        response = self.client.get(reverse("api:ingredients-list"))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_can_list_ingredients_by_name(self):
        """
        Проверяем, что любой пользователь может
        получить список ингредиентов по имени.
        """
        expected_data = [
            {
                "id": self.ingredient_1.id,
                "name": self.ingredient_1.name,
                "measurement_unit": self.ingredient_1.measurement_unit,
            }
        ]
        response = self.client.get(
            reverse("api:ingredients-list"),
            {"name": self.ingredient_1.name[:3]},
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )


class RetrieveIngredientTest(APITestCase):
    def setUp(self):
        self.ingredient = Ingredient.objects.create(
            name="ingredient", measurement_unit="г"
        )

    def test_can_retrieve_ingredient(self):
        """
        Проверяем, что любой пользователь может получить конкретный ингредиент.
        """
        expected_data = {
            "id": self.ingredient.id,
            "name": self.ingredient.name,
            "measurement_unit": self.ingredient.measurement_unit,
        }
        response = self.client.get(
            reverse("api:ingredients-detail", args=[self.ingredient.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_cant_retrive_nonexistent_ingredient(self):
        """
        Проверяем, что любой пользователь не может
        получить несуществующий конкретный тег.
        """
        response = self.client.get(
            reverse("api:ingredients-detail", args=[self.ingredient.id + 1])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"detail": "Страница не найдена."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class ListRecipesTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.tag = Tag.objects.create(name="tag", color="#111111", slug="tag")
        self.ingredient = (
            Ingredient.objects.create(name="ingredient", measurement_unit="г")
        ).__dict__
        self.ingredient["amount"] = 100
        image = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABA"
            "AAAAQCAIAAACQkWg2AAAAAXNSR0IArs4c6QAAAARnQU1BAACxj"
            "wv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZSURBVDhPY/h"
            "PIhjVQAwY1UAMGHQa/v8HAK+t/R8kTA7nAAAAAElFTkSuQmCC"
        )
        self.recipe_1 = Recipe.objects.create(
            author=self.user,
            name="recipe1",
            image=image,
            text="recipetext",
            cooking_time=45,
        )
        self.recipe_1.tags.set([self.tag.id])
        create_ingredients([self.ingredient], self.recipe_1)
        self.recipe_2 = Recipe.objects.create(
            author=self.user,
            name="recipe2",
            image=image,
            text="recipetext",
            cooking_time=45,
        )
        self.recipe_2.tags.set([self.tag.id])
        create_ingredients([self.ingredient], self.recipe_2)

    def test_can_list_recipes(self):
        """
        Проверяем, что любой пользователь можетт получить список рецептов.
        """
        expected_data = [
            {
                "id": self.recipe_1.id,
                "tags": [
                    {
                        "id": self.tag.id,
                        "name": self.tag.name,
                        "color": self.tag.color,
                        "slug": self.tag.slug,
                    }
                ],
                "author": {
                    "username": self.user.username,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "id": self.user.id,
                    "email": self.user.email,
                    "is_subscribed": False,
                },
                "ingredients": [
                    {
                        "id": self.ingredient.get("id"),
                        "name": self.ingredient.get("name"),
                        "measurement_unit": self.ingredient.get(
                            "measurement_unit"
                        ),
                        "amount": self.ingredient.get("amount"),
                    }
                ],
                "is_in_shopping_cart": False,
                "is_favorited": False,
                "name": self.recipe_1.name,
                "image": "http://testserver" + self.recipe_1.image.url,
                "text": self.recipe_1.text,
                "cooking_time": self.recipe_1.cooking_time,
            },
            {
                "id": self.recipe_2.id,
                "tags": [
                    {
                        "id": self.tag.id,
                        "name": self.tag.name,
                        "color": self.tag.color,
                        "slug": self.tag.slug,
                    }
                ],
                "author": {
                    "username": self.user.username,
                    "first_name": self.user.first_name,
                    "last_name": self.user.last_name,
                    "id": self.user.id,
                    "email": self.user.email,
                    "is_subscribed": False,
                },
                "ingredients": [
                    {
                        "id": self.ingredient.get("id"),
                        "name": self.ingredient.get("name"),
                        "measurement_unit": self.ingredient.get(
                            "measurement_unit"
                        ),
                        "amount": self.ingredient.get("amount"),
                    }
                ],
                "is_in_shopping_cart": False,
                "is_favorited": False,
                "name": self.recipe_2.name,
                "image": "http://testserver" + self.recipe_2.image.url,
                "text": self.recipe_2.text,
                "cooking_time": self.recipe_2.cooking_time,
            },
        ]
        response = self.client.get(reverse("api:recipes-list"))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data.get("results"),
            expected_data,
            "Тело ответа API не соответствует документации",
        )


class RetrieveRecipeTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.tag = Tag.objects.create(name="tag", color="#111111", slug="tag")
        self.ingredient = (
            Ingredient.objects.create(name="ingredient", measurement_unit="г")
        ).__dict__
        self.ingredient["amount"] = 100
        self.ingredient.pop("_state")
        image = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABA"
            "AAAAQCAIAAACQkWg2AAAAAXNSR0IArs4c6QAAAARnQU1BAACxj"
            "wv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZSURBVDhPY/h"
            "PIhjVQAwY1UAMGHQa/v8HAK+t/R8kTA7nAAAAAElFTkSuQmCC"
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            name="recipe1",
            image=image,
            text="recipetext",
            cooking_time=45,
        )
        self.recipe.tags.set([self.tag.id])
        create_ingredients([self.ingredient], self.recipe)
        self.tag = self.tag.__dict__
        self.tag.pop("_state")

    def test_can_retrieve_recipe(self):
        """
        Проверяем, что любой пользователь может получить конкретный рецепт.
        """
        expected_data = {
            "id": self.recipe.id,
            "tags": [self.tag],
            "author": {
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "id": self.user.id,
                "email": self.user.email,
                "is_subscribed": False,
            },
            "ingredients": [self.ingredient],
            "is_in_shopping_cart": False,
            "is_favorited": False,
            "name": self.recipe.name,
            "image": "http://testserver" + self.recipe.image.url,
            "text": self.recipe.text,
            "cooking_time": self.recipe.cooking_time,
        }

        response = self.client.get(
            reverse("api:recipes-detail", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_can_retrieve_nonexistent_recipe(self):
        """
        Проверяем, что любой пользователь не может
        получить конкретный несуществующий рецепт.
        """
        response = self.client.get(
            reverse("api:recipes-detail", args=[self.recipe.id + 1])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"detail": "Страница не найдена."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class CreateRecipeTest(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.tag_1 = Tag.objects.create(
            name="tag1", color="#111111", slug="tag1"
        ).__dict__
        self.tag_2 = Tag.objects.create(
            name="tag2", color="#222222", slug="tag2"
        ).__dict__
        self.tag_1.pop("_state")
        self.tag_2.pop("_state")
        self.ingredient_1 = Ingredient.objects.create(
            name="ingredient1", measurement_unit="г"
        ).__dict__
        self.ingredient_2 = Ingredient.objects.create(
            name="ingredient2", measurement_unit="г"
        ).__dict__
        self.ingredient_1.pop("_state")
        self.ingredient_2.pop("_state")
        self.amount_1 = 100
        self.amount_2 = 200
        self.image = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABA"
            "AAAAQCAIAAACQkWg2AAAAAXNSR0IArs4c6QAAAARnQU1BAACxj"
            "wv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZSURBVDhPY/h"
            "PIhjVQAwY1UAMGHQa/v8HAK+t/R8kTA7nAAAAAElFTkSuQmCC"
        )
        self.request_data = {
            "ingredients": [
                {"id": self.ingredient_1.get("id"), "amount": self.amount_1},
                {"id": self.ingredient_2.get("id"), "amount": self.amount_2},
            ],
            "tags": [self.tag_1.get("id"), self.tag_2.get("id")],
            "image": self.image,
            "name": "recipe",
            "text": "recipetext",
            "cooking_time": 45,
        }
        self.client = APIClient()

    def test_auth_can_create_recipe(self):
        """
        Проверяем, что аутентифицированный пользователь может создать рецепт.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:recipes-list"), self.request_data
        )
        self.ingredient_1["amount"] = self.amount_1
        self.ingredient_2["amount"] = self.amount_2
        expected_data = {
            "id": 1,
            "tags": [self.tag_1, self.tag_2],
            "author": {
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "id": self.user.id,
                "email": self.user.email,
                "is_subscribed": False,
            },
            "ingredients": [self.ingredient_1, self.ingredient_2],
            "is_in_shopping_cart": False,
            "is_favorited": False,
            "name": self.request_data.get("name"),
            "image": "http://testserver/media/temp.png",
            "text": self.request_data.get("text"),
            "cooking_time": self.request_data.get("cooking_time"),
        }
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Запрос возвращает не 201 код",
        )
        self.assertEqual(
            Recipe.objects.all().count(),
            1,
            "Рецепт не создается в базе данных",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauth_cant_create_recipe(self):
        """
        Проверяем, что неаутентифицированный пользователь
        не может создать рецепт.
        """
        response = self.client.post(
            reverse("api:recipes-list"), self.request_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_cant_create_recipe_with_nonexistent_items(self):
        """
        Проверяем, что пользователь не может создать рецепт
        с несуществующими тегами или ингредиентами.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        new_request_data = deepcopy(self.request_data)
        new_request_data["tags"] = [123, 321]
        response = self.client.post(
            reverse("api:recipes-list"), new_request_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertIn(
            "tags",
            response.data,
            "Тело ответа API не соответствует документации",
        )
        new_request_data = deepcopy(self.request_data)
        new_request_data["ingredients"] = [
            {"id": self.ingredient_1.get("id") + 123, "amount": self.amount_1}
        ]
        response = self.client.post(
            reverse("api:recipes-list"), new_request_data
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"ingredients": "Такой ингредиент не существует."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class UpdateRecipeTest(APITestCase):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.other_user = User.objects.create(
            username="other_user",
            email="other_user@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.other_token = Token.objects.create(user=self.other_user)
        self.tag = Tag.objects.create(name="tag", color="#111111", slug="tag")
        self.other_tag = Tag.objects.create(
            name="other_tag", color="#222222", slug="other-tag"
        ).__dict__
        self.other_tag.pop("_state")
        self.ingredient = (
            Ingredient.objects.create(name="ingredient", measurement_unit="г")
        ).__dict__
        self.ingredient["amount"] = 100
        self.ingredient.pop("_state")
        self.other_ingredient = (
            Ingredient.objects.create(
                name="other_ingredient", measurement_unit="г"
            )
        ).__dict__
        self.other_ingredient["amount"] = 200
        self.other_ingredient.pop("_state")
        self.image = (
            "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABA"
            "AAAAQCAIAAACQkWg2AAAAAXNSR0IArs4c6QAAAARnQU1BAACxj"
            "wv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAAZSURBVDhPY/h"
            "PIhjVQAwY1UAMGHQa/v8HAK+t/R8kTA7nAAAAAElFTkSuQmCC"
        )
        self.recipe = Recipe.objects.create(
            author=self.user,
            name="recipe",
            image=self.image,
            text="recipetext",
            cooking_time=45,
        )
        self.recipe.tags.set([self.tag.id])
        create_ingredients([self.ingredient], self.recipe)
        self.request_data = {
            "ingredients": [
                {
                    "id": self.other_ingredient.get("id"),
                    "amount": self.other_ingredient.get("amount"),
                }
            ],
            "tags": [self.other_tag.get("id")],
            "image": self.image,
            "name": "recipe",
            "text": "recipetext",
            "cooking_time": 45,
        }
        self.client = APIClient()

    def test_author_can_update_recipe(self):
        """
        Проверяем, что автор может отредактировать свой рецепт.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        expected_data = {
            "id": self.recipe.id,
            "tags": [self.other_tag],
            "author": {
                "username": self.user.username,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "id": self.user.id,
                "email": self.user.email,
                "is_subscribed": False,
            },
            "ingredients": [self.other_ingredient],
            "is_in_shopping_cart": False,
            "is_favorited": False,
            "name": self.request_data.get("name"),
            "image": "http://testserver/media/temp.png",
            "text": self.request_data.get("text"),
            "cooking_time": self.request_data.get("cooking_time"),
        }
        response = self.client.patch(
            reverse("api:recipes-detail", args=[self.recipe.id]),
            self.request_data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauth_cant_update_recipe(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может отредактировать рецепт.
        """
        response = self.client.patch(
            reverse("api:recipes-detail", args=[self.recipe.id]),
            self.request_data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauthor_cant_update_recipe(self):
        """
        Проверяем, что не автор не может отредактировать рецепт.
        """
        self.client.credentials(
            HTTP_AUTHORIZATION="Token " + self.other_token.key
        )
        response = self.client.patch(
            reverse("api:recipes-detail", args=[self.recipe.id]),
            self.request_data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Запрос возвращает не 403 код",
        )
        self.assertEqual(
            {
                "detail": "У вас недостаточно прав "
                          "для выполнения данного действия."
            },
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_author_cant_update_recipe_with_nonexistent_items(self):
        """
        Проверяем, что автор не может отредактировать рецепт,
        используя несуществующие теги или ингредиенты.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        new_request_data = deepcopy(self.request_data)
        new_request_data["tags"] = [123, 321]
        response = self.client.patch(
            reverse("api:recipes-detail", args=[self.recipe.id]),
            new_request_data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertIn(
            "tags",
            response.data,
            "Тело ответа API не соответствует документации",
        )
        new_request_data = deepcopy(self.request_data)
        new_request_data["ingredients"] = [
            {
                "id": self.ingredient.get("id") + 123,
                "amount": self.ingredient.get("amount"),
            }
        ]
        response = self.client.patch(
            reverse("api:recipes-detail", args=[self.recipe.id]),
            new_request_data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"ingredients": "Такой ингредиент не существует."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_author_cant_update_recipe_with_uncorrect_data(self):
        """
        Проверяем, что автор не может отредактировать рецепт,
        используя некорретные данные.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        new_request_data = deepcopy(self.request_data)
        new_request_data["ingredients"] = [
            {"id": self.ingredient.get("id") + 123, "amount": -100}
        ]
        response = self.client.patch(
            reverse("api:recipes-detail", args=[self.recipe.id]),
            new_request_data,
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertIn(
            "ingredients",
            response.data,
            "Тело ответа API не соответствует документации",
        )


class DeleteRecipe(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.other_user = User.objects.create(
            username="other_user",
            email="other_user@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user, name="recipe", text="recipetext", cooking_time=45
        )
        self.other_recipe = Recipe.objects.create(
            author=self.other_user,
            name="other_recipe",
            text="other_recipetext",
            cooking_time=45,
        )
        self.client = APIClient()

    def test_author_can_delete_recipe(self):
        """
        Проверяем, что автор может удалить свой рецепт.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-detail", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Запрос возвращает не 204 код",
        )
        self.assertEqual(
            Recipe.objects.all().count(),
            1,
            "Рецепт не удаляется из базы данных",
        )

    def test_noauth_cant_delete_recipe(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может удалить рецепт.
        """
        response = self.client.delete(
            reverse("api:recipes-detail", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            Recipe.objects.all().count(),
            2,
            "Рецепт всё равно удалился из базы данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauthor_cant_delete_recipe(self):
        """
        Проверяем, что не автор не может удалить рецепт.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-detail", args=[self.other_recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
            "Запрос возвращает не 403 код",
        )
        self.assertEqual(
            Recipe.objects.all().count(),
            2,
            "Рецепт всё равно удалился из базы данных",
        )
        self.assertEqual(
            {
                "detail": "У вас недостаточно прав "
                          "для выполнения данного действия."
            },
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_author_cant_delete_nonexistent_recipe(self):
        """
        Проверяем, что автор не может удалить несущетсвующий рецепт.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-detail", args=[self.other_recipe.id + 1])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            "Запрос возвращает не 404 код",
        )
        self.assertEqual(
            {"detail": "Страница не найдена."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class AddFavorite(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user, name="recipe", text="recipetext", cooking_time=45
        )
        self.client = APIClient()

    def test_auth_user_can_add_recipe_to_favorites(self):
        """
        Проверяем, что аунтифицированный пользователь
        может добавить рецепт в избранное.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        expected_data = {
            "id": self.recipe.id,
            "name": self.recipe.name,
            "image": None,
            "cooking_time": self.recipe.cooking_time,
        }
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Запрос возвращает не 201 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )
        self.assertEqual(
            Favorite.objects.all().count(),
            1,
            "Запись о добавлении пользователем рецепта "
            "в избранное не создаётся в базе данных",
        )

    def test_noauth_user_cant_add_recipe_to_favorites(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может добавить рецепт в избранное.
        """
        response = self.client.post(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            Favorite.objects.all().count(),
            0,
            "Запись о добавлении пользователем рецепта "
            "всё равно создаётся в базе данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_add_existent_recipe_to_favorites(self):
        """
        Проверяем, что аунтифицированный пользователь
        не может добавить рецепт в избранное дважды.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        response = self.client.post(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Рецепт уже в избранном"},
            "Тело ответа API не соответствует документации",
        )


class DeleteFavorite(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user, name="recipe", text="recipetext", cooking_time=45
        )
        self.favorite = Favorite.objects.create(
            user=self.user, recipe=self.recipe
        )
        self.client = APIClient()

    def test_auth_user_can_delete_recipe_from_favorites(self):
        """
        Проверяем, что аунтифицированны пользователь
        может удалить рецепт из списка избранного.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Запрос возвращает не 204 код",
        )
        self.assertEqual(
            Favorite.objects.all().count(),
            0,
            "Запись о добавлении пользователем "
            "рецепта не удалилась из базы данных",
        )

    def test_noauth_user_cant_delete_recipe_from_favorites(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может удалить рецепт из списка избранного.
        """
        response = self.client.delete(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            Favorite.objects.all().count(),
            1,
            "Запись о добавлении пользователем рецепта "
            "всё равно удалилась из базы данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_delete_nonexistent_recipe_from_favorites(self):
        """
        Проверяем, что аунтифицированный пользователь
        не может удалить рецепт из избранного, если его там нет.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        response = self.client.delete(
            reverse("api:recipes-favorite", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Такого рецепта нет в избранном"},
            "Тело ответа API не соответствует документации",
        )


class AddShoppingCart(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user, name="recipe", text="recipetext", cooking_time=45
        )
        self.client = APIClient()

    def test_auth_user_can_add_recipe_to_shopping_cart(self):
        """
        Проверяем, что аунтифицированный пользователь
        может добавить рецепт в список покупок.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        expected_data = {
            "id": self.recipe.id,
            "name": self.recipe.name,
            "image": None,
            "cooking_time": self.recipe.cooking_time,
        }
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Запрос возвращает не 201 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )
        self.assertEqual(
            ShoppingCart.objects.all().count(),
            1,
            "Запись о добавлении пользователем рецепта "
            "в избранное не создаётся в базе данных",
        )

    def test_noauth_user_cant_add_recipe_to_shopping_cart(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может добавить рецепт в список покупок.
        """
        response = self.client.post(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            ShoppingCart.objects.all().count(),
            0,
            "Запись о добавлении пользователем рецепта "
            "всё равно создаётся в базе данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_add_existent_recipe_to_shopping_cart(self):
        """
        Проверяем, что аунтифицированный пользователь
        не может добавить рецепт в список покупок дважды.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        response = self.client.post(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Рецепт уже в списке покупок"},
            "Тело ответа API не соответствует документации",
        )


class DeleteFavorite(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user, name="recipe", text="recipetext", cooking_time=45
        )
        self.shopping_cart = ShoppingCart.objects.create(
            user=self.user, recipe=self.recipe
        )
        self.client = APIClient()

    def test_auth_user_can_delete_recipe_from_shopping_cart(self):
        """
        Проверяем, что аунтифицированны пользователь
        может удалить рецепт из списка покупок.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Запрос возвращает не 204 код",
        )
        self.assertEqual(
            ShoppingCart.objects.all().count(),
            0,
            "Запись о добавлении пользователем рецепта "
            "не удалилась из базы данных",
        )

    def test_noauth_user_cant_delete_recipe_from_shopping_cart(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может удалить рецепт из списка покупок.
        """
        response = self.client.delete(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            ShoppingCart.objects.all().count(),
            1,
            "Запись о добавлении пользователем рецепта "
            "всё равно удалилась из базы данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_delete_nonexistent_recipe_from_shopping_cart(self):
        """
        Проверяем, что аунтифицированный пользователь
        не может удалить рецепт из списка покупок, если его там нет.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        response = self.client.delete(
            reverse("api:recipes-shopping_cart", args=[self.recipe.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Такого рецепта нет в списке покупок"},
            "Тело ответа API не соответствует документации",
        )


class AddSubscribe(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.other_user = User.objects.create(
            username="other_user",
            email="other_user@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.other_user,
            name="recipe",
            text="recipetext",
            cooking_time=45,
        )
        self.client = APIClient()

    def test_auth_user_can_subscribe(self):
        """
        Проверяем, что аунтифицированный пользователь
        может подписаться на другого пользователя.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        expected_data = {
            "email": self.other_user.email,
            "id": self.other_user.id,
            "username": self.other_user.username,
            "first_name": self.other_user.first_name,
            "last_name": self.other_user.last_name,
            "recipes": [
                {
                    "id": self.recipe.id,
                    "name": self.recipe.name,
                    "image": None,
                    "cooking_time": self.recipe.cooking_time,
                }
            ],
            "is_subscribed": True,
            "recipes_count": self.other_user.recipes.count(),
        }
        response = self.client.post(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
            "Запрос возвращает не 201 код",
        )
        self.assertEqual(
            response.data,
            expected_data,
            "Тело ответа API не соответствует документации",
        )
        self.assertEqual(
            Subscribe.objects.all().count(),
            1,
            "Запись о добавлении пользователем рецепта "
            "в избранное не создаётся в базе данных",
        )

    def test_noauth_user_cant_subscribe(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может подписаться на другого пользователя.
        """
        response = self.client.post(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            Subscribe.objects.all().count(),
            0,
            "Запись о добавлении пользователем рецепта "
            "всё равно создаётся в базе данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_add_existent_subscribe(self):
        """
        Проверяем, что аунтифицированный пользователь
        не может подписаться на другого пользователя дважды.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        response = self.client.post(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Вы уже подписаны на автора"},
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_subscribe_yourself(self):
        """
        Проверяем, что аунтифицированный пользователь
        не может подписаться на самого себя.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.post(
            reverse("api:users-subscribe", args=[self.user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Вы не можете подписаться на себя"},
            "Тело ответа API не соответствует документации",
        )


class DeleteSubscribe(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.other_user = User.objects.create(
            username="other_user",
            email="other_user@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.other_user,
            name="recipe",
            text="recipetext",
            cooking_time=45,
        )
        self.subscribe = Subscribe.objects.create(
            subscriber=self.user, author=self.other_user
        )
        self.client = APIClient()

    def test_auth_user_can_unsubscribe(self):
        """
        Проверяем, что аунтифицированный пользователь
        может отписаться от другого пользователя.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
            "Запрос возвращает не 204 код",
        )
        self.assertEqual(
            Subscribe.objects.all().count(),
            0,
            "Запись о добавлении пользователем рецепта "
            "не удалилась из базы данных",
        )

    def test_noauth_user_cant_unsubscribet(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может отписаться от другого пользователя.
        """
        response = self.client.delete(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            Subscribe.objects.all().count(),
            1,
            "Запись о добавлении пользователем рецепта "
            "всё равно удалилась из базы данных",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )

    def test_auth_user_cant_delete_nonexistent_subscribe(self):
        """
        Проверяем, что аунтифицированный пользователь не может
        отписаться от другого пользователя, если он не подписан.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.delete(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        response = self.client.delete(
            reverse("api:users-subscribe", args=[self.other_user.id])
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
            "Запрос возвращает не 400 код",
        )
        self.assertEqual(
            response.data,
            {"errors": "Вы не были подписаны на автора"},
            "Тело ответа API не соответствует документации",
        )


class ListSubscriptions(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.other_user_1 = User.objects.create(
            username="other_user_1",
            email="other_user_1@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.other_user_2 = User.objects.create(
            username="other_user_2",
            email="other_user_2@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe_1 = Recipe.objects.create(
            author=self.other_user_1,
            name="recipe",
            text="recipetext",
            cooking_time=45,
        )
        self.recipe_2 = Recipe.objects.create(
            author=self.other_user_2,
            name="recipe",
            text="recipetext",
            cooking_time=45,
        )
        self.subscribe_1 = Subscribe.objects.create(
            subscriber=self.user, author=self.other_user_1
        )
        self.subscribe_2 = Subscribe.objects.create(
            subscriber=self.user, author=self.other_user_2
        )
        self.client = APIClient()

    def test_auth_user_can_show_subscriptions(self):
        """
        Проверяем, что аунтифицированный пользователь
        может проверить свои подписки.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        expected_data = [
            {
                "email": self.other_user_1.email,
                "id": self.other_user_1.id,
                "username": self.other_user_1.username,
                "first_name": self.other_user_1.first_name,
                "last_name": self.other_user_1.last_name,
                "is_subscribed": True,
                "recipes": [
                    {
                        "id": self.recipe_1.id,
                        "name": self.recipe_1.name,
                        "image": None,
                        "cooking_time": self.recipe_1.cooking_time,
                    }
                ],
                "recipes_count": self.other_user_1.recipes.count(),
            },
            {
                "email": self.other_user_2.email,
                "id": self.other_user_2.id,
                "username": self.other_user_2.username,
                "first_name": self.other_user_2.first_name,
                "last_name": self.other_user_2.last_name,
                "is_subscribed": True,
                "recipes": [
                    {
                        "id": self.recipe_2.id,
                        "name": self.recipe_2.name,
                        "image": None,
                        "cooking_time": self.recipe_2.cooking_time,
                    }
                ],
                "recipes_count": self.other_user_2.recipes.count(),
            },
        ]
        response = self.client.get(reverse("api:users-subscriptions"))
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.data.get("results"),
            expected_data,
            "Тело ответа API не соответствует документации",
        )

    def test_noauth_user_cant_show_subscriptions(self):
        """
        Проверяем, что неаунтифицированный пользователь
        не может проверить подписки.
        """
        response = self.client.get(reverse("api:users-subscriptions"))
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )


class DownloadShoppingCart(APITestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="test",
            email="test@mail.ru",
            first_name="Test",
            last_name="Testov",
        )
        self.token = Token.objects.create(user=self.user)
        self.recipe = Recipe.objects.create(
            author=self.user, name="recipe", text="recipetext", cooking_time=45
        )
        self.shopping_cart = ShoppingCart.objects.create(
            user=self.user, recipe=self.recipe
        )
        self.client = APIClient()

    def test_auth_user_can_download_shopping_cart(self):
        """
        Проверяем, что аунтифицированнный пользователь
        может скачать список покупок.
        """
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)
        response = self.client.get(
            reverse("api:recipes-download_shopping_cart")
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
            "Запрос возвращает не 200 код",
        )
        self.assertEqual(
            response.headers.get("Content-Type"),
            "text/plain; charset=utf-8",
            "Запрос не инициализирует загрузку текстового файла",
        )

    def test_auth_user_can_download_shopping_cart(self):
        """
        Проверяем, что неаунтифицированнный пользователь
        не может скачать список покупок.
        """
        response = self.client.get(
            reverse("api:recipes-download_shopping_cart")
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Запрос возвращает не 401 код",
        )
        self.assertEqual(
            {"detail": "Учетные данные не были предоставлены."},
            response.data,
            "Тело ответа API не соответствует документации",
        )
