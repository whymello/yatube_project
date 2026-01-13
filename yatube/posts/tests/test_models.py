from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title = 'Тестовая группа',
            slug = 'Тестовый слаг',
            description = 'Тестовое описание'
        )
        cls.post = Post.objects.create(
            text = 'Тестовый пост, работает ли?',
            author = cls.user
        )

    def test_models_have_correct_object_names(self) -> None:
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.post
        group = PostModelTest.group
        field_object_names = {
            post: post.text[:15],
            group: group.title
        }

        for field, object_name in field_object_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    str(field),
                    object_name,
                    f'Метод __str__ модели {field.__class__.__name__} работает неправильно.'
                )

    def test_verbose_name(self) -> None:
        """Проверяем, что verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verbose_name.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self) -> None:
        """Проверяем, что help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
