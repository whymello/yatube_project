from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import Post, Group
from .forms import PostForm


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

    title = f'{group.title} | Yatube'

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

    post_list = Post.objects.filter(author=author).order_by('-pub_date')
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
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

@login_required
def post_create(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    template = 'posts/create_post.html'
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)  # Создаём объект, но не сохраняем в БД
            post.author = request.user  # Добавляем в поле author значение текущего user
            post.save() # Теперь сохраняем запись в БД
            return redirect('posts:profile', username=request.user.username) # Перенаправляем пользователя на его страницу профиля
        context = {
            'form': form,
        }
        return render(request, template, context)
    form = PostForm()
    context = {
        'form': form,
    }
    return render(request, template, context)

@login_required
def post_edit(request: HttpRequest, post_id: int):
    template = 'posts/create_post.html'
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post) # Связываем с существующим объектом
        if form.is_valid():
            form.save() # Cохраняем изменения записи в БД
            return redirect('posts:post_detail', post_id=post_id) # Перенаправляем пользователя на изменённый пост
        context = {
            'form': form,
            'is_edit': is_edit,
        }
        return render(request, template, context)
    form = PostForm(instance=post) # Предзаполняем данными из поста
    context = {
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)
