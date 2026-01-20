from django.test import TestCase


class CoreViewTests(TestCase):
    """Docstring for CoreViewTests."""

    def test_core_view_error_page(self) -> None:
        """Docstring for test_core_view_error_page."""
        template = 'core/404.html'
        url = '/nonexist-page/'
        response = self.client.get(path=url)

        # * Проверка, что статус ответа сервера - 404
        self.assertEqual(response.status_code, 404)
        # * Проверка, что используется шаблон core/404.html
        self.assertTemplateUsed(response, template)
