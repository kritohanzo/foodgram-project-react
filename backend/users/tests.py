from rest_framework.test import APITestCase
from users.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

class CreateUserTest(APITestCase):
    def test_can_create_user(self):
        '''Проверяем, что пользователь может зарегистрироваться.'''
        request_data = {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov', 'password': 'mysecretpassword'}
        response = self.client.post(reverse('api:users-list'), request_data)
        expected_data = {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov', 'id': 1}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Запрос возвращает не 201 код")
        self.assertEqual(User.objects.all().count(), 1, "Пользователь не создается в базе данных")
        self.assertEqual(response.data, expected_data, "Тело ответа API не соответствует документации")

class TokenUserTest(APITestCase):
    def setUp(self):
        user_data = {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov'}
        self.user = User.objects.create(**user_data)
        self.user.set_password('mysecretpassword')
        self.user.save()
    
    def test_can_get_token(self):
        '''Проверяем, что зарегистрированный пользователь может получить токен.'''
        request_data = {'email': 'test@mail.ru', 'password': 'mysecretpassword'}
        response = self.client.post(reverse('api:token_login'), request_data)
        expected_data = {'auth_token': Token.objects.get(user=self.user).key}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Запрос возвращает не 201 код")
        self.assertEqual(Token.objects.all().count(), 1, "Токен не создается в базе данных")
        self.assertEqual(response.data, expected_data, "Тело ответа API не соответствует документации")


# class UserTests(APITestCase):
    # def test_user_create_account(self):
    #     """
    #     Проверяем, что пользователь может создать аккаунт.
    #     """
    #     url = 'http://127.0.0.1:8000/api/users/'
    #     data = {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov', 'password': 'mysecretpassword'}
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 201)
    #     self.assertEqual(response.data, {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov', 'id': 1})

    # def test_user_get_token(self):
    #     """
    #     Проверяем, что пользователь может получить токен.
    #     """
    #     url = 'http://127.0.0.1:8000/api/auth/token/login/'
    #     data = {'email': 'test@mail.ru', 'password': 'mysecretpassword'}
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, 201)
