from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post


User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title = 'Тестовая группа',
            slug = 'test-path',
            description = 'Тестовое описание'
        )
        cls.author = User.objects.create_user(username='test_author')
        cls.user = User.objects.create_user(username='test_user')
        cls.post = Post.objects.create(
            text = 'Тестовый пост',
            author = cls.author,
            group = cls.group
        )

    def setUp(self) -> None:
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        self.author = Client()
        self.author.force_login(PostsURLTests.author)
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)

    def test_posts_url(self) -> None:
        guest_client = self.guest_client
        author = self.author
        authorized_client = self.authorized_client
        post_id = PostsURLTests.post.pk
        status_code_200 = HTTPStatus.OK.value
        status_code_403 = HTTPStatus.FORBIDDEN.value
        status_code_404 = HTTPStatus.NOT_FOUND.value

        addresses_user_status_code = {
            '/': {'type_user': guest_client, 'status_code': status_code_200},
            '/group/test-path/': {'type_user': guest_client, 'status_code': status_code_200},
            '/profile/test_author/': {'type_user': guest_client, 'status_code': status_code_200},
            f'/posts/{post_id}/': {'type_user': guest_client, 'status_code': status_code_200},
            f'/posts/{post_id}/edit/': {'type_user': author, 'status_code': status_code_200},
            f'/posts/{post_id}/edit/': (
                {'type_user': authorized_client, 'status_code': status_code_403}),
            '/create/': {'type_user': authorized_client, 'status_code': status_code_200},
            '/unexisting_page/': {'type_user': guest_client, 'status_code': status_code_404}
        }

        for address, user_code in addresses_user_status_code.items():
            with self.subTest(address=address):
                self.assertEqual(
                    user_code['type_user'].get(address).status_code,
                    user_code['status_code']
                )

    def test_posts_url_redirect(self) -> None:
        post_id = PostsURLTests.post.pk
        addresses_redirect = {
            f'/posts/{post_id}/edit/': f'/auth/login/?next=/posts/{post_id}/edit/',
            '/create/': '/auth/login/?next=/create/'
        }

        for address, redirect in addresses_redirect.items():
            with self.subTest(address=address):
                self.assertRedirects(
                    self.guest_client.get(address, follow=True),
                    redirect
                )

    def test_posts_url_uses_correct_template(self) -> None:
        post_id = PostsURLTests.post.pk
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-path/': 'posts/group_list.html',
            '/profile/test_author/': 'posts/profile.html',
            f'/posts/{post_id}/': 'posts/post_detail.html',
            f'/posts/{post_id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.author.get(address),
                    template
                )
