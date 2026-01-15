from http import HTTPStatus

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self) -> None:
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_users_url(self) -> None:
        guest_client = self.guest_client
        status_code_200 = HTTPStatus.OK.value

        addresses_user_status_code = {
            '/auth/signup/': {'type_user': guest_client, 'status_code': status_code_200}
        }

        for address, user_code in addresses_user_status_code.items():
            with self.subTest(address=address):
                self.assertEqual(
                    user_code['type_user'].get(address).status_code,
                    user_code['status_code']
                )

    def test_users_url_uses_correct_template(self) -> None:
        templates_url_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            # f'/auth/reset/{uidb64}/{token}/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.authorized_client.get(address),
                    template
                )

    def test_users_url_uses_correct_template_post(self) -> None:
        templates_url_names = {
            '/auth/logout/': 'users/logged_out.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.authorized_client.post(address),
                    template
                )
