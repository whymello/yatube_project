"""Тесты приложения about."""

from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


# Create your tests here.
class AboutURLTests(TestCase):
    """Тестирование URLs приложения."""

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_url(self) -> None:
        """Проверка доступности url."""
        urls = ('/about/author/', '/about/tech/')
        status_code_200 = HTTPStatus.OK.value

        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(path=url)
                self.assertEqual(response.status_code, status_code_200)

    def test_about_url_uses_correct_template(self) -> None:
        """Проверка названия используемого шаблона для url."""
        url_template = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.guest_client.get(path=url)
                self.assertTemplateUsed(response, template)


class AboutViewTests(TestCase):
    """Тестирование Views приложения."""

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_about_view_uses_correct_template(self) -> None:
        """Проверка названия используемого шаблона для view."""
        # * Собираем в словарь пары "reverse(view_name): имя_html_шаблона"
        url_template = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

        # * Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for url, template in url_template.items():
            with self.subTest(url=url):
                response = self.guest_client.get(path=url)
                self.assertTemplateUsed(response, template)
