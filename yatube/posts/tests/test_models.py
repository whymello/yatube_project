"""Тесты Models приложения posts."""

from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post


User = get_user_model()


class PostsModelTests(TestCase):
    """Тестирование Models приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Amelia')
        cls.group = Group.objects.create(
            title='Laudantium aut ut quae numquam.',
            slug='suscipit-qui-sed',
            description='Delectus qui sint maiores iste voluptas.',
        )
        cls.post = Post.objects.create(
            text='In maxime perferendis ut voluptatem quis quam maxime.',
            author=cls.user,
            group=cls.group,
        )

    def test_posts_model_have_correct_object_names(self) -> None:
        """Проверка корректного имени объекта model."""
        post = PostsModelTests.post
        group = PostsModelTests.group

        field_object_name = {post: post.text[:15], group: group.title}

        for field, object_name in field_object_name.items():
            with self.subTest(field=field):
                self.assertEqual(str(field), object_name)

    def test_posts_model_have_correct_verbose_name(self) -> None:
        """Проверка корректного verbose_name поля model."""
        post = PostsModelTests.post
        field_verbose_name = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка',
        }
        for field, verbose_name in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name, verbose_name)

    def test_posts_model_have_correct_help_text(self) -> None:
        """Проверка корректного help_text поля model."""

        post = PostsModelTests.post
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу',
        }
        for field, help_text in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).help_text, help_text)
