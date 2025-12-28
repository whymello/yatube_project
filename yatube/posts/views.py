from django.shortcuts import render
from django.http import HttpRequest, HttpResponse


# Create your views here.
def index(request: HttpRequest) -> HttpResponse:
    return HttpResponse('Главная страница')

def group_posts(request: HttpRequest, slug) -> HttpResponse:
    return HttpResponse(f'Посты по теме {slug}')
