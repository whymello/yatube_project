from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    """View функция страницы ошибки 404."""
    # * Переменная exception содержит отладочную информацию;
    # * выводить её в шаблон пользователской страницы 404 мы не станем
    template = 'core/404.html'
    title = 'Custom 404'
    context = {'title': title, 'path': request.path}

    return render(request, template, context, status=404)

def server_error(request: HttpRequest) -> HttpResponse:
    """View функция страницы ошибки 500."""
    template = 'core/500.html'
    title = 'Custom 500'
    context = {'title': title}

    return render(request, template, context, status=500)

def permission_denied(request: HttpRequest, exception) -> HttpResponse:
    """View функция страницы ошибки 403."""
    template = 'core/403.html'
    title = 'Custom 403'
    context = {'title': title}

    return render(request, template, context, status=403)

def csrf_failure(request: HttpRequest, reason='') -> HttpResponse:
    """View функция страницы ошибки 403csrf."""
    template = 'core/403csrf.html'
    title = 'Custom CSRF check error'
    context = {'title': title}

    return render(request, template, context)
