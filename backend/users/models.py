from django.db import models
from django.contrib.auth.models import AbstractUser
from enum import Enum

class RoleChoiser(Enum):
    USER = "user"
    ADMIN = "admin"

    @classmethod
    def choices(cls):
        return tuple((role.name, role.value) for role in cls)

class User(AbstractUser):
    username = models.CharField(verbose_name="Логин", max_length=150, unique=True)
    email = models.EmailField(verbose_name="Почта", max_length=254, unique=True)
    first_name = models.CharField(verbose_name="Имя", max_length=150)
    last_name = models.CharField(verbose_name="Фамилия", max_length=150)
    role = models.CharField(verbose_name="Роль", max_length=100, choices=RoleChoiser.choices(), default=RoleChoiser.USER.name)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    @property
    def is_user(self):
        return self.role == RoleChoiser.USER.name
    
    @property
    def is_admin(self):
        return any([self.role == RoleChoiser.ADMIN.name, self.is_stuff])
    
    class Meta:
        verbose_name_plural = "Пользователи"
        verbose_name = "Пользователь"
        ordering = ("username",)
        constraints = [
            models.UniqueConstraint(
                fields=["username", "email"], name="unique_username_email"
            )
        ]

    def __str__(self):
        return self.username
    
class Subscribe(models.Model):
    subscriber = models.ForeignKey(verbose_name="Подписчик", to=User, on_delete=models.CASCADE, related_name='subscriptions_subscriber')
    author = models.ForeignKey(verbose_name="Автор", to=User, on_delete=models.CASCADE, related_name='subscriptions_author')

    class Meta:
        verbose_name_plural = "Подписки"
        verbose_name = "Подписка"
        ordering = ("id",)
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "author"], name="unique_subscriber_author"
            )
        ]

    def __call__(self):
        return self
