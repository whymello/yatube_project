from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


User = get_user_model()


# * Создадим собственный класс для формы регистрации
# * Сделаем его наследником предустановленного класса UserCreationForm
class CreationForm(UserCreationForm):
    """Форма для регистрации пользователей."""

    class Meta(UserCreationForm.Meta):
        # * Укажем модель, с которой связана создаваемая форма
        model = User
        # * Укажем, какие поля должны быть видны в форме и в каком порядке
        fields = ("first_name", "last_name", "username", "email")
