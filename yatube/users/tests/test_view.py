from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms


User = get_user_model()


# Create your tests here.
class UsersViewTests(TestCase):
    def setUp(self) -> None:
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он авторизован.
        self.user = User.objects.create_user(
            username='test_user',
            email='test.example.com',
            password='password123'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self) -> None:
        """Проверка того, что URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'): 'users/password_change_form.html',
            reverse('users:password_change_done'): 'users/password_change_done.html',
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse('users:password_reset_done'): 'users/password_reset_done.html',
            # reverse('users:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token}
            # ): 'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'): 'users/password_reset_complete.html'
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_post(self) -> None:
        """Проверка того, что URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('users:logout'): 'users/logged_out.html',
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.post(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_users_signup_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон signup сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('users:signup'))

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(key='form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
