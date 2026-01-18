from django.views.generic import CreateView

# * Функция reverse_lazy позволяет получить URL по параметрам функции path()
from django.urls import reverse_lazy

from .forms import CreationForm


# Create your views here.
class SignUp(CreateView):
    """Docstring for SignUp."""

    form_class = CreationForm

    # * После успешной регистрации перенаправляем пользователя на главную.
    success_url = reverse_lazy("posts:index")
    template_name = "users/signup.html"
