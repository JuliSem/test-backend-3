from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class Role(models.TextChoices):
    TEACHER = 'TEACHER', 'Преподаватель'
    STUDENT = 'STUDENT', 'Студент'


class CustomUser(AbstractUser):
    """Кастомная модель пользователя - студента."""

    role = models.CharField(
        'Роль',
        max_length=30,
        choices=Role.choices,
        default=Role.STUDENT
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=250,
        unique=True
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('-id',)

    def __str__(self):
        return self.get_full_name()


class Balance(models.Model):
    """Модель баланса пользователя."""

    user = models.ForeignKey(
        CustomUser,
        verbose_name='Пользователь',
        on_delete=models.CASCADE
    )
    balance = models.DecimalField(
        verbose_name='Баланс (баллы)',
        max_digits=8,
        decimal_places=2,
        default=1000
    )

    def save(self, *args, **kwargs):
        if self.balance < 0:
            raise ValidationError(
                message='Баланс не может быть отрицательным!'
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Баланс'
        verbose_name_plural = 'Балансы'
        ordering = ('-id',)

    def __str__(self):
        return f'Пользователь: {self.user.username} | Баланс: {self.balance}'
