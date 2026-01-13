from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self) -> None:
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self) -> None:
        # Отправляем запрос через client,
        # созданный в setUp()
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_author(self) -> None:
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_tech(self) -> None:
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)
