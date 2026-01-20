"""Тесты Forms приложения posts."""

import tempfile
import shutil

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Group, Post


# * Создаем временную папку для медиа-файлов;
# * на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


# * Для сохранения media-файлов в тестах будет использоваться
# * временная папка TEMP_MEDIA_ROOT, а потом удаляться
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormTests(TestCase):
    """Тестирование Forms приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Abdul')
        cls.group = Group.objects.create(
            title='sit enim rerum',
            slug='consequuntur-corrupti-accusantium',
            description='Saepe vel incidunt eius ea aut.',
        )
        cls.post = Post.objects.create(
            text='Dolor hic praesentium.', author=cls.user, group=cls.group
        )

        # * Для тестирования загрузки изображений
        # * берём байт-последовательность картинки,
        # * состоящей из двух пикселей: белого и чёрного
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff\x21\xf9\x04\x00\x00'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0c'
            b'\x0a\x00\x3b'
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()

        # * Модуль shutil - библиотека Python с удобными инструментами
        # * для управления файлами и директориями:
        # * создание, удаление, копирование, перемещение, изменение папок и файлов
        # * Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.author = Client()
        self.author.force_login(PostsFormTests.user)
        self.group = PostsFormTests.group
        self.count_posts = Post.objects.count()

        self.uploaded = SimpleUploadedFile(
            name='small.gif', content=PostsFormTests.small_gif, content_type='image/gif'
        )

    def test_posts_form_create_post(self) -> None:
        """Проверка создания поста через form."""
        # * Подсчитаем количество записей в Post
        form_data = {
            'text': 'Rem at consequatur quis quis suscipit.',
            'group': self.group.pk,
            'image': self.uploaded,
        }
        self.author.post(path=reverse('posts:post_create'), data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), self.count_posts + 1)

    def test_posts_form_edit_post(self) -> None:
        """Проверка редактирования поста через form."""
        post = PostsFormTests.post
        form_data = {
            'text': 'Officiis qui dolorum.',
            'group': self.group.pk,
            'image': self.uploaded,
        }
        self.author.post(
            path=reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        # * Обновляем объект из БД
        post.refresh_from_db()
        self.assertEqual(Post.objects.count(), self.count_posts)
        self.assertEqual(post.text, 'Officiis qui dolorum.')
