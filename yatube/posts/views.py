from django.shortcuts import render, get_object_or_404, redirect
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


User = get_user_model()


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    """View функция главной страницы."""
    template = "posts/index.html"
    title = "Последние обновления на сайте"

    # * Одна строка вместо тысячи слов на SQL:
    # * в переменную posts будет сохранена выборка из 10 объектов модели Post,
    # * отсортированных по полю pub_date по убыванию (от больших значений к меньшим)
    post_list = Post.objects.prefetch_related("author", "group").all()
    # * Показывать по 10 записей на странице.
    paginator = Paginator(post_list, 10)

    # * Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")

    # * Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    # * В словаре context отправляем информацию в шаблон
    context = {"title": title, "page_obj": page_obj}

    return render(request, template, context)


# * View-функция для страницы сообщества:
def group_posts(request: HttpRequest, slug) -> HttpResponse:
    """View функция страниц /group/<slug>/."""
    template = "posts/group_list.html"

    # * Функция get_object_or_404 получает по заданным критериям объект
    # * из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # * В нашем случае в переменную group будут переданы объекты модели Group,
    # * поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    title = f"{group.title} | Yatube"

    # * Метод .filter позволяет ограничить поиск по критериям.
    # * Это аналог добавления
    # * условия WHERE group_id = {group_id}
    post_list = Post.objects.prefetch_related("author").filter(group=group)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"title": title, "group": group, "page_obj": page_obj}

    return render(request, template, context)


def profile(request: HttpRequest, username: str) -> HttpResponse:
    """View функция страниц /profile/<username>/."""
    template = "posts/profile.html"

    author = get_object_or_404(User, username=username)
    post_list = Post.objects.prefetch_related("group").filter(author=author)

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user, author=author).exists()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"author": author, "page_obj": page_obj, "following": following}

    return render(request, template, context)


def post_detail(request: HttpRequest, post_id: int) -> HttpResponse:
    """View функция страниц /posts/<post_id>/."""
    template = "posts/post_detail.html"

    post = Post.objects.select_related("author", "group").get(id=post_id)
    title = f"Пост {post.text[:30]}"
    form = CommentForm(request.POST or None)
    comments = Comment.objects.select_related("author").filter(post=post_id)

    context = {"title": title, "post": post, "form": form, "comments": comments}

    return render(request, template, context)


@login_required
def post_create(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    """View функция страницы /create/."""
    template = "posts/create_post.html"

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)  # * Создаём объект, но не сохраняем в БД
        # * Добавляем в поле author значение текущего user
        post.author = request.user
        post.save()  # * Теперь сохраняем запись в БД

        # * Перенаправляем пользователя на его страницу профиля
        return redirect("posts:profile", username=request.user.username)

    context = {
        "form": form,
    }

    return render(request, template, context)


@login_required
def post_edit(request: HttpRequest, post_id: int) -> HttpResponseRedirect | HttpResponse:
    """View функция страницы /posts/<post_id>/edit/."""
    template = "posts/create_post.html"
    is_edit = True
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    form = PostForm(
        # * Связываем с существующим объектом
        request.POST or None,
        files=request.FILES or None,
        # * Предзаполняем данными из поста
        instance=post,
    )

    if form.is_valid():
        form.save()  # * Cохраняем изменения записи в БД

        # * Перенаправляем пользователя на изменённый пост
        return redirect("posts:post_detail", post_id=post_id)

    context = {
        "post": post,
        "form": form,
        "is_edit": is_edit,
    }

    return render(request, template, context)


@login_required
def post_delete(request: HttpRequest, post_id: int) -> HttpResponseRedirect:
    """View функция страницы /posts/<post_id>/delete/."""
    post = get_object_or_404(Post, id=post_id)

    if request.user != post.author:
        return redirect("posts:post_detail", post_id=post_id)

    post.delete()

    # * Перенаправляем пользователя на главную страницу
    return redirect("posts:index")


@login_required
def add_comment(request: HttpRequest, post_id: int) -> HttpResponseRedirect:
    """View функция страницы /posts/<post_id>/comment/."""
    # * Получаем пост
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)  # * Создаём объект, но не сохраняем в БД
        # * Добавляем в поле author значение текущего user
        comment.author = request.user
        comment.post = post
        comment.save()  # * Теперь сохраняем запись в БД

    # * Перенаправляем пользователя на страницу комментируемого поста
    return redirect("posts:post_detail", post_id=post_id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    """View функция страницы /follow/."""
    template = "posts/follow.html"
    title = "Последние посты избранных авторов"

    subscriptions = Follow.objects.filter(user=request.user).values_list("author", flat=True)
    post_list = Post.objects.prefetch_related("author", "group").filter(author__in=subscriptions)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"title": title, "page_obj": page_obj}

    return render(request, template, context)


@login_required
def profile_follow(request: HttpRequest, username) -> HttpResponseRedirect:
    """View функция страницы /profile/<username>/follow/."""
    author = get_object_or_404(User, username=username)

    if request.user == author:
        # * Перенаправляем пользователя на страницу автора
        return redirect("posts:profile", username=username)

    following = Follow.objects.filter(user=request.user, author=author).exists()

    if not following:
        Follow.objects.create(user=request.user, author=author)

    # * Перенаправляем пользователя на страницу автора
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request: HttpRequest, username) -> HttpResponseRedirect:
    """View функция страницы /profile/<username>/unfollow/."""
    author = get_object_or_404(User, username=username)

    if request.user == author:
        # * Перенаправляем пользователя на страницу автора
        return redirect("posts:profile", username=username)

    Follow.objects.filter(user=request.user, author=author).delete()

    # * Перенаправляем пользователя на страницу автора
    return redirect("posts:profile", username=username)
