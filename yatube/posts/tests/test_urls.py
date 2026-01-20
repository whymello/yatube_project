"""Тесты URLs приложения posts."""

from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post


User = get_user_model()


class PostsURLTests(TestCase):
    """Тестирование URLs приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.author = User.objects.create_user(username='Melissa')
        cls.user = User.objects.create_user(username='Kelvin')
        cls.group = Group.objects.create(
            title='cupiditate assumenda tempora',
            slug='nulla-laborum-pariatur',
            description='Aut iusto enim quae accusamus ex.',
        )
        cls.post = Post.objects.create(
            text='Eos assumenda quaerat.', author=cls.author, group=cls.group
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostsURLTests.author)
        self.post_id = PostsURLTests.post.pk
        self.status_code_200 = HTTPStatus.OK.value
        self.slug = PostsURLTests.group.slug
        self.username = PostsURLTests.author.username

    def test_posts_url_guest_client(self) -> None:
        """Проверка доступности url неавторизованным пользователем."""
        status_code_404 = HTTPStatus.NOT_FOUND.value
        url_status_code = {
            '/': self.status_code_200,
            f'/group/{self.slug}/': self.status_code_200,
            f'/profile/{self.username}/': self.status_code_200,
            f'/posts/{self.post_id}/': self.status_code_200,
            '/unexisting_page/': status_code_404,
        }

        for url, status_code in url_status_code.items():
            with self.subTest(url=url):
                response = self.guest_client.get(path=url)
                self.assertEqual(response.status_code, status_code)

    def test_posts_url_author(self) -> None:
        """Проверка доступности url /posts/<post_id>/edit/ автору поста."""
        url = f'/posts/{self.post_id}/edit/'
        response = self.author.get(url)

        self.assertEqual(response.status_code, self.status_code_200)

    def test_posts_url_authorized_client(self) -> None:
        """Проверка доступности '/create/' авторизованным пользователем."""
        authorized_client = PostsURLTests.authorized_client
        url = '/create/'
        response = authorized_client.get(path=url)

        self.assertEqual(response.status_code, self.status_code_200)

    def test_posts_url_redirect_authorized_client(self) -> None:
        """Проверка редиректа авторизованного пользователя
        с /posts/<post_id>/edit/ на /posts/<post_id>/."""
        authorized_client = PostsURLTests.authorized_client
        url = f'/posts/{self.post_id}/edit/'
        redirect = f'/posts/{self.post_id}/'
        response = authorized_client.get(path=url, follow=True)

        self.assertRedirects(response, redirect)

    def test_posts_url_redirect_guest_client(self) -> None:
        """Проверка редиректа неавторизованного пользователя с url на страницу /auth/login/."""
        url_redirect = {
            f'/posts/{self.post_id}/edit/': f'/auth/login/?next=/posts/{self.post_id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }

        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(path=url, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_url_redirect(self) -> None:
        """Проверка редиректа неавторизованного пользователя с url на страницу /auth/login/."""
        url_redirect = {
            f'/posts/{self.post_id}/edit/': f'/auth/login/?next=/posts/{self.post_id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }

        for url, redirect in url_redirect.items():
            with self.subTest(url=url):
                response = self.guest_client.get(path=url, follow=True)
                self.assertRedirects(response, redirect)

    def test_posts_url_uses_correct_template(self) -> None:
        """Проверка названия используемого шаблона для url."""
        url_template = {
            '/': 'posts/index.html',
            f'/group/{self.slug}/': 'posts/group_list.html',
            f'/profile/{self.username}/': 'posts/profile.html',
            f'/posts/{self.post_id}/': 'posts/post_detail.html',
            f'/posts/{self.post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.author.get(url)
                self.assertTemplateUsed(response, template)
