"""Тесты Views приложения posts."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms

from posts.models import Group, Post


User = get_user_model()


class PostsViewTests(TestCase):
    """Тестирование Views приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Barbara')
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
                text=f'Тестовый пост {i}', author=cls.user, group=cls.group
            )
        cls.post = Post.objects.create(
            text='Тестовый пост 13', author=cls.user, group=cls.group
        )

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.group = PostsViewTests.group
        self.user = PostsViewTests.user
        self.post = PostsViewTests.post

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
        url = reverse('posts:index')
        response = self.guest_client.get(path=url)

        self.assertEqual(
            response.context.get(key='title'), 'Последние обновления на сайте'
        )

    def test_posts_view_group_posts_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста group_posts view."""
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

    def test_posts_view_profile_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста profile view."""
        url = reverse('posts:profile', kwargs={'username': self.user.username})
        response = self.guest_client.get(path=url)

        self.assertEqual(response.context.get(key='author'), self.user)

    def test_posts_view_post_detail_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста post_detail view."""
        url = reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        response = self.guest_client.get(path=url)
        fields = ('text', 'author', 'group')

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

    def test_posts_view_first_page_contains_ten_records(self) -> None:
        """Проверка первой страницы paginator передаваемой в контекст view."""
        name_url_kwargs = {
            'index': {},
            'group_posts': {'slug': self.group.slug},
            'profile': {'username': self.user.username},
        }

        for name_url, kwargs in name_url_kwargs.items():
            url = reverse(f'posts:{name_url}', kwargs=kwargs)
            response = self.guest_client.get(path=url)
            # * Проверка: количество постов на первой странице равно 10.
            self.assertEqual(len(response.context.get(key='page_obj')), 10)

    def test_posts_view_second_page_contains_three_records(self) -> None:
        """Проверка второй страницы paginator передаваемой в контекст view."""
        name_url_kwargs = {
            'index': {},
            'group_posts': {'slug': self.group.slug},
            'profile': {'username': self.user.username},
        }

        for name_url, kwargs in name_url_kwargs.items():
            url = reverse(f'posts:{name_url}', kwargs=kwargs)
            response = self.guest_client.get(path=url + '?page=2')
            # * Проверка: количество постов на второй странице равно 3.
            self.assertEqual(len(response.context.get(key='page_obj')), 3)

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
            # * Проверка: пост post находится на выбранной странице
            self.assertIn(self.post, response.context.get(key='page_obj').object_list)

    def test_posts_view_post_not_on_group_pages(self) -> None:
        """Проверка отсутствия поста у view другой group_posts."""
        group2 = PostsViewTests.group2
        url = reverse('posts:group_posts', kwargs={'slug': group2.slug})
        response = self.guest_client.get(path=url)

        # * Проверка: пост post не находится на выбранной странице
        self.assertNotIn(self.post, response.context.get(key='page_obj').object_list)
