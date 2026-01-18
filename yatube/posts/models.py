from django.db import models
from django.contrib.auth import get_user_model


# Create your models here.
User = get_user_model()


class Group(models.Model):
    """Модель Group для хранения групп постов."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return str(self.title)


class Post(models.Model):
    """Модель Post для хранения постов."""

    text = models.TextField(verbose_name="Текст поста", help_text="Введите текст поста")
    pub_date = models.DateTimeField(verbose_name="Дата публикации", auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts", verbose_name="Автор"
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name="posts",
        verbose_name="Группа",
        blank=True,
        null=True,
        help_text="Выберите группу",
    )

    def __str__(self) -> str:
        # Выводим текст поста
        return str(self.text)[:15]
