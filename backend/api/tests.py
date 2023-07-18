from rest_framework.test import APITestCase
from users.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from requests.auth import HTTPBasicAuth
from rest_framework.test import APIClient

class CreateUserTest(APITestCase):
    def test_can_create_user(self):
        '''Проверяем, что пользователь может зарегистрироваться.'''
        request_data = {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov', 'password': 'mysecretpassword'}
        response = self.client.post(reverse('api:users-list'), request_data)
        expected_data = {'email': 'test@mail.ru', 'username': 'test', 'first_name': 'Test', 'last_name': 'Testov', 'id': 1}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Запрос возвращает не 201 код")
        self.assertEqual(User.objects.all().count(), 1, "Пользователь не создается в базе данных")
        self.assertEqual(response.data, expected_data, "Тело ответа API не соответствует документации")

class CreataTokenTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@mail.ru', username='test')
        self.user_password = 'mysecretpassword'
        self.user.set_password(self.user_password)
        self.user.save()
        self.token_count = Token.objects.all().count()

    def test_can_get_token(self):
        '''Проверяем, что зарегистрированный пользователь может получить токен.'''
        request_data = {'email': self.user.email, 'password': self.user_password}
        response = self.client.post(reverse('api:token_login'), request_data)
        token_count = Token.objects.all().count()
        expected_data = {'auth_token': Token.objects.get(user=self.user).key}
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, "Ответ API содержит не 201 код")
        self.assertEqual(token_count, self.token_count+1, "Токен не создается в базе данных")
        self.assertEqual(response.data, expected_data, "Тело ответа API не соответствует документации")

class DestroyTokenTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email='test@mail.ru', username='test')
        self.user.set_password('mysecretpassword')
        self.user.save()
        self.token = Token.objects.create(user=self.user)
        self.token_count = Token.objects.all().count()
        self.client = APIClient()

    def test_can_destroy_token(self):
        '''Проверяем, что зарегистрированный пользователь может уничтожить свой токен.'''
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(reverse('api:token_logout'))
        token_count = Token.objects.all().count()
        expected_data = None
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT, "Ответ API содержит не 204 код")
        self.assertEqual(token_count, self.token_count-1, "Токен не удаляется из базы данных")
        self.assertEqual(response.data, expected_data, "Тело ответа API не соответствует документации")
