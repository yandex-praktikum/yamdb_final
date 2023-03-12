from django.contrib.auth.models import AbstractUser
from django.core.validators import (MaxValueValidator, MinValueValidator,
                                    RegexValidator)
from django.db import models
import hashlib

from .validators import year_validator

USER = 'user'
ADMIN = 'admin'
MODERATOR = 'moderator'

ROLE_CHOICES = [
    (USER, USER),
    (ADMIN, ADMIN),
    (MODERATOR, MODERATOR),
]


class User(AbstractUser):
    USERNAME_VALIDATOR = RegexValidator(r'^[\w.@+-]+\z')
    username = models.CharField(
        validators=[USERNAME_VALIDATOR],
        verbose_name='Имя',
        max_length=150,
        unique=True,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True,
    )
    is_active = models.BooleanField(
        verbose_name='Активирован ли', default=False
    ),
    bio = models.TextField(verbose_name='Биография', blank=True, null=True)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff is True

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def activated(self):
        return self.is_active is True

    class Meta:
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_hash(self):
        constant_data = str(self.id) + str(self.date_joined)
        return hashlib.md5(constant_data.encode()).hexdigest()


class Category(models.Model):
    SLUG_VALIDATOR = RegexValidator(r'^[-a-zA-Z0-9_]+$')
    name = models.CharField(verbose_name='Название категории', max_length=256)
    slug = models.SlugField(
        validators=[SLUG_VALIDATOR],
        verbose_name='Слаг категории',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(verbose_name='Имя жанра', max_length=256)
    slug = models.SlugField(
        verbose_name='Слаг жанра',
        max_length=50,
        unique=True
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(verbose_name='Название', max_length=256)
    year = models.IntegerField(
        verbose_name='Дата выхода', validators=[year_validator]
    )
    description = models.TextField(
        verbose_name='Описание', null=True, blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория',
        null=True,
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre, related_name='titles', verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title, verbose_name='Произведение', on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre, verbose_name='Жанр', on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title}, жанр - {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.CharField(max_length=100)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
    )
    score = models.IntegerField(
        verbose_name='Рейтинг',
        validators=(MinValueValidator(1), MaxValueValidator(10)),
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=(
                    'title',
                    'author',
                ),
                name='unique review',
            )
        ]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.CharField(verbose_name='Текст комментария', max_length=200)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text
