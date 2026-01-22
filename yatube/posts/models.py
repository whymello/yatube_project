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
    # * Поле для картинки (необязательное)
    image = models.ImageField(
        verbose_name='Картинка',
        # * Аргумент upload_to указывает директорию,
        # * в которую будут загружаться пользовательские файлы.
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self) -> str:
        # Выводим текст поста
        return str(self.text)[:15]


class Comment(models.Model):
    """Модель Comment для хранения комментариев к постам."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(verbose_name='Текст', help_text='Текст нового комментария')
    created = models.DateTimeField(verbose_name='Дата создания', auto_now_add=True)


class Follow(models.Model):
    """Модель Follow для хранения подписок на авторов."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
