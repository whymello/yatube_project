"""Тесты Views приложения posts."""

import tempfile
import shutil

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from posts.models import Group, Post, Follow


# * Создаем временную папку для медиа-файлов;
# * на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


User = get_user_model()


# * Для сохранения media-файлов в тестах будет использоваться
# * временная папка TEMP_MEDIA_ROOT, а потом удаляться
@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewTests(TestCase):
    """Тестирование Views приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Barbara')
        cls.user2 = User.objects.create_user(username='Mae')
        cls.author = User.objects.create_user(username='Alene')
        cls.group = Group.objects.create(
            title='amet rem vitae',
            slug='delectus-dignissimos-vero',
            description='Sit illo sunt fugiat quas neque nulla velit.',
        )
        cls.group2 = Group.objects.create(
            title='fugiat ut eaque',
            slug='omnis-impedit-iure',
            description='Dicta dolor porro autem delectus beatae ea et.',
        )
        for i in range(1, 13):
            Post.objects.create(
                text=f'{i} Тестовый пост', author=cls.user, group=cls.group
            )
        for i in range(14, 20):
            Post.objects.create(
                text=f'{i} Тестовый пост', author=cls.author, group=cls.group2
            )

        # * Для тестирования загрузки изображений
        # * берём байт-последовательность картинки,
        # * состоящей из двух пикселей: белого и чёрного
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xff\xff\xff\x21\xf9\x04\x00\x00'
            b'\x00\x00\x00\x2c\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0c'
            b'\x0a\x00\x3b'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='13 Тестовый пост', author=cls.user, group=cls.group, image=uploaded
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
        self.user = PostsViewTests.user
        self.user2 = PostsViewTests.user2

        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(self.user2)

        self.group = PostsViewTests.group
        self.post = PostsViewTests.post

    def tearDown(self) -> None:
        cache.clear()
        super().tearDown()

    def test_posts_view_uses_correct_template(self) -> None:
        """Проверка названия используемого шаблона для view."""
        # * Собираем в словарь пары "reverse(view_name): имя_html_шаблона"
        url_template = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }

        # * Проверяем, что при обращении к url вызывается соответствующий HTML-шаблон
        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(path=url)
                self.assertTemplateUsed(response, template)

    def test_posts_view_index_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста index view."""
        post_list = list(Post.objects.all())
        url = reverse('posts:index')
        response = self.guest_client.get(path=url)

        self.assertEqual(
            response.context.get(key='title'), 'Последние обновления на сайте'
        )

        self.assertEqual(
            response.context.get(key='page_obj').object_list, post_list[:10]
        )
        self.assertEqual(
            response.context.get(key='page_obj').object_list[0].image, self.post.image
        )

        self.assertEqual(len(response.context.get(key='page_obj')), len(post_list[:10]))
        response = self.guest_client.get(path=url + '?page=2')
        self.assertEqual(
            len(response.context.get(key='page_obj')), len(post_list[10:20])
        )

    def test_posts_view_group_posts_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста group_posts view."""
        post_list = list(Post.objects.filter(group=self.group))
        url = reverse('posts:group_posts', kwargs={'slug': self.group.slug})
        response = self.guest_client.get(path=url)
        fields = ('title', 'slug', 'description')

        self.assertEqual(
            response.context.get(key='title'), f'{self.group.title} | Yatube'
        )

        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context.get(key='group'), field),
                    getattr(self.group, field),
                )

        self.assertEqual(
            response.context.get(key='page_obj').object_list, post_list[:10]
        )
        self.assertEqual(
            response.context.get(key='page_obj').object_list[0].image, self.post.image
        )

        self.assertEqual(len(response.context.get(key='page_obj')), len(post_list[:10]))
        response = self.guest_client.get(path=url + '?page=2')
        self.assertEqual(
            len(response.context.get(key='page_obj')), len(post_list[10:20])
        )

    def test_posts_view_profile_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста profile view."""
        post_list = list(Post.objects.filter(author=self.user))
        url = reverse('posts:profile', kwargs={'username': self.user.username})
        response = self.guest_client.get(path=url)

        self.assertEqual(response.context.get(key='author'), self.user)

        self.assertEqual(
            response.context.get(key='page_obj').object_list, post_list[:10]
        )
        self.assertEqual(
            response.context.get(key='page_obj').object_list[0].image, self.post.image
        )

        self.assertEqual(len(response.context.get(key='page_obj')), len(post_list[:10]))
        response = self.guest_client.get(path=url + '?page=2')
        self.assertEqual(
            len(response.context.get(key='page_obj')), len(post_list[10:20])
        )

    def test_posts_view_post_detail_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста post_detail view."""
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.guest_client.get(path=url)
        fields = ('text', 'author', 'group', 'image')

        self.assertEqual(
            response.context.get(key='title'), f'Пост {self.post.text[:30]}'
        )

        for field in fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context.get(key='post'), field),
                    getattr(self.post, field),
                )

    def test_posts_view_post_create_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста post_create view."""
        url = reverse('posts:post_create')
        response = self.authorized_client.get(path=url)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # * Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for field, type_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get(key='form').fields.get(field)
                # * Проверяет, что поле формы является экземпляром
                # * указанного класса
                self.assertIsInstance(form_field, type_field)

    def test_posts_view_post_edit_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста post_edit view."""
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(path=url)

        self.assertTrue(response.context.get(key='is_edit'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        # * Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for field, type_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get(key='form').fields.get(field)
                # * Проверяет, что поле формы является экземпляром
                # * указанного класса
                self.assertIsInstance(form_field, type_field)

    def test_posts_view_post_on_index_group_profile_pages(self) -> None:
        """Проверка нахождения поста у view index, profile и соответсвующей group_posts."""
        name_url_kwargs = {
            'index': {},
            'group_posts': {'slug': self.group.slug},
            'profile': {'username': self.user.username},
        }

        for name_url, kwargs in name_url_kwargs.items():
            url = reverse(f'posts:{name_url}', kwargs=kwargs)
            response = self.guest_client.get(path=url)

            with self.subTest(url=url):
                # * Проверка: пост post находится на выбранной странице
                self.assertIn(
                    self.post, response.context.get(key='page_obj').object_list
                )

    def test_posts_view_post_not_on_group_pages(self) -> None:
        """Проверка отсутствия поста у view другой group_posts."""
        group2 = PostsViewTests.group2
        url = reverse('posts:group_posts', kwargs={'slug': group2.slug})
        response = self.guest_client.get(path=url)

        # * Проверка: пост post не находится на выбранной странице
        self.assertNotIn(self.post, response.context.get(key='page_obj').object_list)

    def test_posts_view_index_correct_uses_cache(self) -> None:
        """Проверка кеширования страницы index."""
        url = reverse('posts:index')
        response = self.guest_client.get(path=url)

        # * Проверка: пост post находится на главной странице
        self.assertContains(response, self.post.text)

        Post.objects.get(id=self.post.id).delete()
        response = self.guest_client.get(path=url)

        # * Проверка: пост post находится в кеше главной страницы
        self.assertContains(response, self.post.text)

        cache.clear()
        response = self.guest_client.get(path=url)

        # * Проверка: пост post больше нет на главной странице
        self.assertNotContains(response, self.post.text)

    def test_posts_view_follow_unfollow_to_author(self) -> None:
        """Проверка подписки/отписки пользователя на автора."""
        count_follows = Follow.objects.count()
        author = PostsViewTests.author
        url = reverse('posts:profile_follow', kwargs={'username': author.username})
        self.authorized_client.get(path=url)

        self.assertEqual(Follow.objects.count(), count_follows + 1)

        url = reverse('posts:profile_unfollow', kwargs={'username': author.username})
        self.authorized_client.get(path=url)

        self.assertEqual(Follow.objects.count(), count_follows)

    def test_posts_view_follow_index(self) -> None:
        """Проверка наличия/отсутствия поста у подписанных/неподписанных пользователей."""
        author = PostsViewTests.author
        Follow.objects.create(user=self.user, author=author)
        post = Post.objects.create(
            text='Id totam ea vitae adipisci est alias amet.',
            author=author,
        )
        url = reverse('posts:follow_index')
        response1 = self.authorized_client.get(path=url)
        response2 = self.authorized_client2.get(path=url)

        self.assertContains(response1, post.text)
        self.assertNotContains(response2, post.text)
