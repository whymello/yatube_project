"""Тесты Forms приложения users."""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class UsersFormTests(TestCase):
    """Тестирование Forms приложения."""

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Bennie')

    def test_users_form_create_post(self) -> None:
        """Проверка регистрации пользователя через form."""
        # * Подсчитаем количество записей в User
        count_users = User.objects.count()
        form_data = {
            'username': 'Fiona',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        self.guest_client.post(
            path=reverse('users:signup'), data=form_data, follow=True
        )

        self.assertEqual(User.objects.count(), count_users + 1)
