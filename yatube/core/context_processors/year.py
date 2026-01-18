from datetime import date

from django.http import HttpRequest


def year(request: HttpRequest) -> dict[str, int]:
    """Контекст процессор year.

    :param request: Http запрос
    :type request: HttpRequest
    :return: Значение текущего года
    :rtype: dict[str, int]
    """
    return {"year": date.today().year}
