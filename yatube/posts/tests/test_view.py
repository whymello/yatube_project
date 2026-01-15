from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django import forms

from posts.models import Group, Post

User = get_user_model()


class PostsViewTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create_user(username='TestName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Test-address',
            description='Тестовое описание'
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='Test-address-2',
            description='Тестовое описание 2'
        )
        for i in range(1, 13):
            Post.objects.create(
                text=f'Тестовый пост {i}',
                author=cls.user,
                group=cls.group
            )
        cls.post = Post.objects.create(
            text='Тестовый пост 13',
            author=cls.user,
            group=cls.group
        )

    def setUp(self) -> None:
        # Создаем авторизованного клиента
        self.client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self) -> None:
        """Проверка того, что URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_posts', kwargs={'slug': 'Test-address'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'TestName'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': PostsViewTests.post.pk}): (
                'posts/post_detail.html'),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': PostsViewTests.post.pk}): (
                'posts/create_post.html')
        }
        # Проверяем, что при обращении к name вызывается соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы
    def test_index_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))

        self.assertEqual(response.context.get(key='title'), 'Последние обновления на сайте')

    def test_group_posts_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон group_list сформирован с правильным контекстом."""
        group = PostsViewTests.group
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'Test-address'})
        )

        self.assertEqual(response.context.get(key='title'), f'{group.title} | Yatube')
        self.assertEqual(response.context.get(key='group').title, group.title)
        self.assertEqual(response.context.get(key='group').slug, group.slug)
        self.assertEqual(response.context.get(key='group').description, group.description)

    def test_profile_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон profile сформирован с правильным контекстом."""
        author = PostsViewTests.user
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'TestName'})
        )

        self.assertEqual(response.context.get(key='author'), author)

    def test_post_detail_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон post_detail сформирован с правильным контекстом."""
        post = PostsViewTests.post
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': PostsViewTests.post.pk})
        )

        self.assertEqual(response.context.get(key='title'), f'Пост {post.text[:30]}')
        self.assertEqual(response.context.get(key='post').text, post.text)
        self.assertEqual(response.context.get(key='post').author, post.author)
        self.assertEqual(response.context.get(key='post').group, post.group)

    def test_post_create_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(key='form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self) -> None:
        """Проверка того, что шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': PostsViewTests.post.pk})
        )

        self.assertTrue(response.context.get(key='is_edit'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }

        # Проверяем, что типы полей формы в словаре context соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(key='form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self) -> None:
        address_kwargs = {
            'index': {},
            'group_posts': {'slug': 'Test-address'},
            'profile': {'username': 'TestName'}
        }

        for address, kwargs in address_kwargs.items():
            response = self.client.get(reverse(f'posts:{address}', kwargs=kwargs))
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(len(response.context.get(key='page_obj')), 10)

    def test_second_page_contains_three_records(self) -> None:
        address_kwargs = {
            'index': {},
            'group_posts': {'slug': 'Test-address'},
            'profile': {'username': 'TestName'}
        }

        for address, kwargs in address_kwargs.items():
            response = self.client.get(reverse(f'posts:{address}', kwargs=kwargs) + '?page=2')
            # Проверка: на второй странице должно быть три поста.
            self.assertEqual(len(response.context.get(key='page_obj')), 3)

    def test_post_on_index_group_profile_pages(self) -> None:
        """Проверка того, что пост находится на нужных страницах index, group_posts, profile."""
        post = PostsViewTests.post

        address_kwargs = {
            'index': {},
            'group_posts': {'slug': 'Test-address'},
            'profile': {'username': 'TestName'}
        }

        for address, kwargs in address_kwargs.items():
            response = self.client.get(reverse(f'posts:{address}', kwargs=kwargs))
            # Проверка: пост post находится на выбранной странице.
            self.assertIn(post, response.context.get(key='page_obj').object_list)

        response = self.client.get(reverse('posts:group_posts', kwargs={'slug': 'Test-address-2'}))
        # Проверка: пост post не находится на выбранной странице.
        self.assertNotIn(post, response.context.get(key='page_obj').object_list)
