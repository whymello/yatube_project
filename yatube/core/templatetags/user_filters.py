from django import template


# * В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# * добавляем к ним и наш фильтр.
register = template.Library()


@register.filter
def addclass(field, css):
    """Кастомный фильтр для django-шаблонов.

    :param field: Переменная
    :param css: Применяемый к переменной css стиль
    :return: Переменная c применённым css стилем
    """
    return field.as_widget(attrs={"class": css})
