# api_yamdb/reviews/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models

from reviews.validator import validate_year

AUTH_USER = 'user'
MODERATOR = 'moderator'
ADMIN = 'admin'
ROLES_CHOICES = (
    (AUTH_USER, 'Аутентифицированный пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Администратор')
)


class User(AbstractUser):
    bio = models.TextField(
        blank=True,
        max_length=400,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=16,
        choices=ROLES_CHOICES,
        default=AUTH_USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(blank=True, max_length=16,)
    email = models.EmailField(unique=True)

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_admin(self):
        return self.role == ADMIN


class Category(models.Model):
    name = models.CharField(max_length=50,)
    slug = models.SlugField(unique=True, db_index=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=50,)
    slug = models.SlugField(unique=True, db_index=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=50)
    year = models.PositiveSmallIntegerField(validators=(validate_year,))
    description = models.TextField(blank=True)
    genre = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='titles'
    )
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles'
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'],
                                    name='unique_review')
        ]

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text
