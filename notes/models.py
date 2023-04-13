from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(
        db_index=True,
        max_length=255,
        unique=True
    )
    email = models.EmailField(
        db_index=True,
        unique=True
    )

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    def __str__(self) -> str:
        return self.username


class Note(models.Model):
    title = models.CharField(
        max_length=150,
        verbose_name='Заголовок'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        db_index=True,
        related_name='notes'
    )
    text = models.TextField()

    def __str__(self) -> str:
        return self.title