# yatube_project

## Описание

Yatube — это блог-платформа и социальная сеть, где пользователи могут публиковать посты, подписываться на авторов и взаимодействовать с контентом.

Проект находится в стадии активной разработки и будет дополняться по мере его развития.

## Технологии

- Python 3.14
- Django 6.0

## Запуск проекта в dev-режиме

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/whymello/yatube_project.git
    ```

2. Перейдите в папку проекта и создайте виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/bin/activate  # для Linux/Mac
    venv\Scripts\activate     # для Windows
    ```

3. Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Выполните миграции:

    ```bash
    python manage.py migrate
    ```

5. Запустите сервер разработки:

    ```bash
    python manage.py runserver
    ```

    Проект будет доступен по адресу: <http://127.0.0.1:8000/>

## Автор

Galiullin Azat
