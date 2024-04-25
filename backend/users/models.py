from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import EMAIL_MAX_LENGTH, USER_MAX_LENGTH
from users.validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name', 'password')
    username = models.CharField(
        verbose_name='Пользователь',
        validators=(validate_username,),
        max_length=USER_MAX_LENGTH,
        unique=True)
    email = models.EmailField(
        verbose_name='Электронная почта',
        max_length=EMAIL_MAX_LENGTH,
        unique=True)
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=USER_MAX_LENGTH)
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=USER_MAX_LENGTH)

    class Meta:
        ordering = ('username',)
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='followers')
    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following')

    class Meta:
        unique_together = ('user', 'following')