"""Тесты Views приложения users."""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


# Create your tests here.
class UsersViewTests(TestCase):
    """Тестирование Views приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(
            username='Carol', email='test.example.com', password='password123'
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(UsersViewTests.user)

    def test_users_view_uses_correct_template(self) -> None:
        """Проверка названия используемого шаблона для view."""
        # * Собираем в словарь пары "reverse(view_name): имя_html_шаблона"
        url_template = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'): 'users/password_change_form.html',
            reverse('users:password_change_done'): 'users/password_change_done.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'): 'users/password_reset_done.html',
            # reverse(
            #     'users:password_reset_confirm',
            #     kwargs={'uidb64': uidb64, 'token': token},
            # ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }

        # * Проверяем, что при обращении к url вызывается соответствующий HTML-шаблон
        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(path=url)
                self.assertTemplateUsed(response, template)

    def test_users_view_uses_correct_template_post_request(self) -> None:
        """Проверка названия используемого шаблона для view."""
        # * Собираем в словарь пары "reverse(view_name): имя_html_шаблона"
        url = reverse('users:logout')

        # * Проверяем, что при обращении к url вызывается соответствующий HTML-шаблон
        response = self.authorized_client.post(path=url)
        self.assertTemplateUsed(response, 'users/logged_out.html')

    def test_users_view_signup_transmits_correct_context(self) -> None:
        """Проверка передаваемого контекста SignUp view."""
        url = reverse('users:signup')
        response = self.authorized_client.get(path=url)

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
        }

        # * Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for field, type_field in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context.get(key='form').fields.get(field)
                # * Проверяет, что поле формы является экземпляром
                # * указанного класса
                print(f'form_field: {form_field}')
                self.assertIsInstance(form_field, type_field)
