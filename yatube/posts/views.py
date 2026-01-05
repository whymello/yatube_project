from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse

from.models import Post, Group


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    template = 'posts/index.html'

    title = 'Последние обновления на сайте'

    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    posts = Post.objects.order_by('-pub_date')[:10]

    # В словаре context отправляем информацию в шаблон
    context = {
        'title': title,
        'posts': posts
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
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]

    context = {
        'title': title,
        'group': group,
        'posts': posts
    }

    return render(request, template, context)
