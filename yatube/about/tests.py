from http import HTTPStatus

from django.test import TestCase, Client


# Create your tests here.
class AboutURLTests(TestCase):
    def setUp(self) -> None:
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_about_url(self) -> None:
        guest_client = self.guest_client
        status_code_200 = HTTPStatus.OK.value
        addresses = ('/about/author/', '/about/tech/')

        for address in addresses:
            with self.subTest(address=address):
                self.assertEqual(
                    guest_client.get(address).status_code,
                    status_code_200
                )

    def test_about_url_uses_correct_template(self) -> None:
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.guest_client.get(address),
                    template
                )
