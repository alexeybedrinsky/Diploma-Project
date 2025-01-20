Система бронирования столиков в ресторане “Три кота”

Этот проект представляет собой веб-приложение для бронирования столиков в ресторане “Три кота”.

Функциональность
Система бронирования столиков с возможностью выбора даты, времени и количества гостей
Аутентификация пользователей (клиенты и персонал ресторана)
Панель администратора для управления бронированиями, столиками и пользователями
Автоматическое подтверждение или отклонение бронирований в зависимости от доступности столиков
Система обратной связи для клиентов

Технологии
Django 5.1.4
PostgreSQL
Bootstrap 5
Docker (в разработке)

Требования
Python 3.8+
PostgreSQL 12+
Другие зависимости указаны в файле requirements.txt

Зависимости
Проект использует следующие основные пакеты:
Django 5.1.4
psycopg2-binary 2.9.10
djangorestframework 3.15.2
Pillow 11.0.0
pytest 8.2.1
Полный список зависимостей можно найти в файле requirements.txt.

## Установка

1. Клонируйте репозиторий
2. Создайте виртуальное окружение и активируйте его
3. Установите зависимости: `pip install -r requirements.txt`
4. Настройте базу данных PostgreSQL
5. Выполните миграции: `python manage.py migrate`
6. Примените фикстуры: python manage.py loaddata fixtures/tables_fixture.json
7. Запустите сервер разработки: `python manage.py runserver`

Запуск
Запустите сервер разработки: python manage.py runserver
Откройте браузер и перейдите по адресу http://127.0.0.1:8000/

Использование
Для создания бронирования перейдите на главную страницу и выберите “Забронировать столик”
Для входа в административную панель перейдите по адресу http://127.0.0.1:8000/admin/ и используйте учетные данные суперпользователя

