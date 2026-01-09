from datetime import date

from django.http import HttpRequest


def year(request: HttpRequest) -> dict[str, int]:
    return {
        'year': date.today().year
        }
