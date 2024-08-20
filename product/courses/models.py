from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

User = get_user_model()


class Course(models.Model):
    """Модель продукта - курса."""

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
    # author = models.CharField(
    #     max_length=250,
    #     verbose_name='Автор',
    # )
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    start_date = models.DateTimeField(
        auto_now=False,
        auto_now_add=False,
        verbose_name='Дата и время начала курса'
    )
    price = models.DecimalField(
        verbose_name='Цена',
        max_digits=6,
        decimal_places=2
    )

    def save(self, *args, **kwargs):
        if self.price < 0:
            raise ValidationError(
                message='Цена на курс не может быть отрицательной!'
            )
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)

    def __str__(self):
        return f'Курс: {self.title}'


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING)
    is_valid = models.BooleanField(
        verbose_name='Доступ',
        default=False
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'course'],
                name='subscription_unique'
            ),
        ]

    def __str__(self):
        return (f'Пользователь: {self.user.username} '
                f'| Курс: {self.course.title}')


class Lesson(models.Model):
    """Модель урока."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    link = models.URLField(
        max_length=250,
        verbose_name='Ссылка',
    )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ('id',)

    def __str__(self):
        return f'Курс: {self.course.title} | Урок: {self.title}'


class Group(models.Model):
    """Модель группы."""

    title = models.CharField(
        max_length=250,
        verbose_name='Название',
    )
    course = models.ForeignKey(
        Course,
        verbose_name='Продукт',
        on_delete=models.CASCADE,
        related_name='groups'
    )
    count_students = models.IntegerField(
        verbose_name='Количество студентов',
        default=0
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-id',)

    def __str__(self):
        return f'Курс: {self.course.title} | Группа: {self.title}'


class GroupStudents(models.Model):
    """Модель отношения студента к группе."""

    group = models.ForeignKey(
        Group,
        verbose_name='Группа',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        verbose_name='Студент',
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Группа студентов'
        verbose_name_plural = 'Группы студентов'
        ordering = ('-id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'],
                name='group_user_unique'
            ),
        ]

    def __str__(self):
        return (f'Курс: {self.group.course.title} '
                f'| Группа: {self.group.title} '
                f'| Студент: {self.user.username}')
