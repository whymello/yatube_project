from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from .models import Post, Group


User = get_user_model()


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    template = 'posts/index.html'

    title = 'Последние обновления на сайте'

    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    post_list = Post.objects.all().order_by('-pub_date')
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    # В словаре context отправляем информацию в шаблон
    context = {
        'title': title,
        'page_obj': page_obj
    }

    return render(request, template, context)

# View-функция для страницы сообщества:
def group_posts(request: HttpRequest, slug) -> HttpResponse:
    template = 'posts/group_list.html'

    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)

    title = f'Записи сообщества {group.title} | Yatube'

    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    post_list = Post.objects.filter(group=group).order_by('-pub_date')
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'title': title,
        'group': group,
        'page_obj': page_obj
    }

    return render(request, template, context)

def profile(request: HttpRequest, username: str) -> HttpResponse:
    template = 'posts/profile.html'

    author = get_object_or_404(User, username=username)

    full_name = f'{author.get_full_name()}'

    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'full_name': full_name,
        'page_obj': page_obj
    }
    return render(request, template, context)

def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    template = 'posts/post_detail.html'

    post = Post.objects.get(pk=post_id)

    title = f'Пост {post.text[:30]}'

    context = {
        'title': title,
        'post': post
    }
    return render(request, template, context)
