"""Тесты URLs приложения users."""

from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class UsersURLTests(TestCase):
    """Тестирование URLs приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Mavis')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersURLTests.user)

    def test_users_url(self) -> None:
        """Проверка доступности url /auth/signup/."""
        guest_client = UsersURLTests.guest_client
        status_code_200 = HTTPStatus.OK.value
        response = guest_client.get(path='/auth/signup/')

        self.assertEqual(response.status_code, status_code_200)

    def test_users_url_uses_correct_template(self) -> None:
        """Проверка названия используемого шаблона для url."""
        url_template = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            # f'/auth/reset/{uidb64}/{token}/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }

        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(path=url)
                self.assertTemplateUsed(response, template)

    def test_users_url_uses_correct_template_post_request(self) -> None:
        """Проверка названия используемого шаблона для url."""
        url = '/auth/logout/'
        response = self.authorized_client.post(path=url)

        self.assertTemplateUsed(response, 'users/logged_out.html')
