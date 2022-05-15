# reviews/models.py

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from .validators import validate_username, validate_year

USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'

ROLE_CHOICES = (
    (USER, _('Пользователь')),
    (MODERATOR, _('Модератор')),
    (ADMIN, _('Администратор')),
)


class User(AbstractUser):
    username = models.CharField(
        _('Имя пользователя'),
        max_length=150,
        unique=True,
        validators=[validate_username],
    )
    email = models.EmailField(
        _('Адрес электронной почты'),
        max_length=254,
        unique=True,
    )
    confirmation_code = models.CharField(
        _('Проверочный код'),
        max_length=settings.CONFIRMATION_CODE_LENGTH,
        blank=True,
    )
    first_name = models.CharField(
        _('Имя'),
        max_length=150,
        blank=True,
    )
    last_name = models.CharField(
        _('Фамилия'),
        max_length=150,
        blank=True,
    )
    bio = models.TextField(
        _('Биография'),
        blank=True,
    )
    role = models.CharField(
        _('Роль'),
        choices=ROLE_CHOICES,
        max_length=max(len(role) for role, _ in ROLE_CHOICES),
        default=USER,
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    class Meta:
        ordering = ['username']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_staff


class AuthorshipModel(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    text = models.TextField()
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата создания'
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)


class GenreAndCategoryModel(models.Model):
    name = models.CharField(
        _('Название'),
        max_length=256
    )
    slug = models.SlugField(
        _('Идентификатор'),
        unique=True, )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        ordering = ('name',)


class Review(AuthorshipModel):
    """Обзоры."""
    title = models.ForeignKey(
        'Title',
        on_delete=models.CASCADE,
        verbose_name=_('Произведение')
    )
    score = models.IntegerField(
        _('Оценка'),
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
    )

    class Meta(AuthorshipModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique review')
        ]
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        default_related_name = 'reviews'

    def __str__(self):
        return self.text[:20]


class Comment(AuthorshipModel):
    """Комментарии."""
    review = models.ForeignKey(
        'Review', on_delete=models.CASCADE,
        verbose_name=_('Отзыв')
    )

    class Meta(AuthorshipModel.Meta):
        verbose_name = _('Комментарий')
        verbose_name_plural = _('Комментарии')
        default_related_name = 'comments'


class Category(GenreAndCategoryModel):
    """Категории."""

    class Meta(GenreAndCategoryModel.Meta):
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')


class Genre(GenreAndCategoryModel):
    """Жанры."""

    class Meta(GenreAndCategoryModel.Meta):
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')


class Title(models.Model):
    """Произведения."""
    name = models.TextField(
        _('Название'),
    )
    year = models.IntegerField(
        _('Дата выхода'),
        validators=[validate_year]
    )
    description = models.TextField(
        _('Описание'),
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        verbose_name=_('Жанр'),
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name=_('Категория'),
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('Произведение')
        verbose_name_plural = _('Произведения')

    def __str__(self):
        return self.name[:15]
