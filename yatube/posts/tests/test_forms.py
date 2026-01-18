"""Тесты Forms приложения posts."""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class PostsFormTests(TestCase):
    """Тестирование Forms приложения."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='Abdul')
        cls.group = Group.objects.create(
            title='sit enim rerum',
            slug='consequuntur-corrupti-accusantium',
            description='Saepe vel incidunt eius ea aut.',
        )
        cls.post = Post.objects.create(
            text='Dolor hic praesentium.', author=cls.user, group=cls.group
        )

    def setUp(self) -> None:
        self.author = Client()
        self.author.force_login(PostsFormTests.user)
        self.group = PostsFormTests.group
        self.count_posts = Post.objects.count()

    def test_posts_form_create_post(self) -> None:
        """Проверка создания поста через form."""
        # * Подсчитаем количество записей в Post
        form_data = {
            'text': 'Rem at consequatur quis quis suscipit.',
            'group': self.group.pk,
        }
        self.author.post(path=reverse('posts:post_create'), data=form_data, follow=True)
        self.assertEqual(Post.objects.count(), self.count_posts + 1)

    def test_posts_form_edit_post(self) -> None:
        """Проверка редактирования поста через form."""
        post = PostsFormTests.post
        form_data = {'text': 'Officiis qui dolorum.', 'group': self.group.pk}
        self.author.post(
            path=reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True,
        )
        # * Обновляем объект из БД
        post.refresh_from_db()
        self.assertEqual(Post.objects.count(), self.count_posts)
        self.assertEqual(post.text, 'Officiis qui dolorum.')
