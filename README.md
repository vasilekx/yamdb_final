# CI/CD для проекта YaMDb API

![example workflow](https://github.com/vasilekx/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

## Описание

Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории: 'Книги', 'Фильмы', 'Музыка'. Список категорий может быть расширен администратором.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
В каждой категории есть произведения: книги, фильмы или музыка. Например, в категории 'Книги' могут быть произведения 'Винни-Пух и все-все-все' и 'Марсианские хроники', а в категории 'Музыка' — песня 'Давеча' группы 'Насекомые' и вторая сюита Баха.
Произведению может быть присвоен жанр из списка предустановленных. Новые жанры может создавать только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы и ставят произведению оценку в диапазоне от одного до десяти; из пользовательских оценок формируется усреднённая оценка произведения — рейтинг. На одно произведение пользователь может оставить только один отзыв.

## Применяемые технологии
[![Python](https://img.shields.io/badge/Python-3.7-blue?style=flat-square&logo=Python&logoColor=3776AB&labelColor=d0d0d0)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-2.2.16-blue?style=flat-square&logo=Django&logoColor=092E20&labelColor=d0d0d0)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/Django%20REST%20Framework-3.12.4-blue?style=flat-square&logo=Django&logoColor=a30000&labelColor=d0d0d0)](https://www.django-rest-framework.org/)
[![Simple JWT](https://img.shields.io/badge/Simple%20JWT%20-4.7.2-blue?style=flat-square&logo=github&logoColor=4285F4&labelColor=d0d0d0)](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
[![gunicorn](https://img.shields.io/badge/gunicorn-20.0.4-blue?style=flat-square&logo=gunicorn&logoColor=499848&labelColor=d0d0d0)](https://gunicorn.org/)
[![Postgres](https://img.shields.io/badge/Postgres-13.0-blue?style=flat-square&logo=PostgreSQL&logoColor=4169E1&labelColor=d0d0d0)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/Nginx-1.21.3-blue?style=flat-square&logo=NGINX&logoColor=009639&labelColor=d0d0d0)](https://nginx.org/ru/)
[![Docker](https://img.shields.io/badge/Docker-20.10.16-blue?style=flat-square&logo=Docker&logoColor=2496ED&labelColor=d0d0d0)](https://www.docker.com/)
[![Docker-Compose](https://img.shields.io/badge/Docker%20Compose-2.5.0-blue?style=flat-square&logo=Docker&logoColor=2496ED&labelColor=d0d0d0)](https://www.docker.com/)

[![Docker Hub](https://img.shields.io/badge/Docker%20Hub-service-blue?style=flat-square&logo=Docker&logoColor=2496ED&labelColor=d0d0d0)](https://hub.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/GitHub%20Actions-service-blue?style=flat-square&logo=GitHub%20actions&logoColor=2088FF&labelColor=d0d0d0)](https://github.com/features/actions/)
[![Yandex.Cloud](https://img.shields.io/badge/Yandex.Cloud-service-blue?style=flat-square&labelColor=d0d0d0)](https://cloud.yandex.ru/)

## Установка сервиса
Проверьте установлен ли у вас Docker 
```bash
sudo docker -v
```
Если Docker отсутствует, то необходимо его [установить](https://docs.docker.com/engine/install/). Вместе с Docker также устанавливается Docker Compose. После установки, проверьте установлена ли у вас Docker Compose версии 2.5.0 или новее:
```bash
sudo docker-compose -v
```
Если версия Docker Compose ниже 2.5.0 необходимо [обновить Docker Compose](https://docs.docker.com/compose/install/).


Клонировать репозиторий:
```bash
git clone git@github.com:vasilekx/yamdb_final.git
```
Перейти в папку infra 
```bash
cd infra
```
Cоздать в директории файл .env со следующими параметрами:
```python
DB_ENGINE=django.db.backends.postgresql # указываем, что работаем с postgresql
POSTGRES_DB=postgres_db_1 # имя базы данных
POSTGRES_USER=postgres_user_1 # логин для подключения к базе данных
POSTGRES_PASSWORD=qawsed123456 # пароль для подключения к БД (установите свой)
DB_HOST=db # название сервиса (контейнера)
DB_PORT=5432 # порт для подключения к БД
DJANGO_SECRET_KEY='DJANGO_SECRET_KEY' # секретный ключ Django
DJANGO_ALLOWED_HOSTS='web localhost 127.0.0.1 [::1]' # cписок хостов/доменов, для которым доступен проект
```
Создать и запустить контейнеры: 
```bash
sudo docker-compose up -d
```
[***Обзор команд*** ](https://docs.docker.com/compose/reference/)*для работы с docker-compose.*

Выполнить миграции:
```bash
sudo docker-compose exec web python manage.py migrate
```
Создать суперпользователя:
```bash
sudo docker-compose exec web python manage.py createsuperuser
```
Собирать статические файлы:
```bash
sudo docker-compose exec web python manage.py collectstatic --no-input
```
Заполнить базу данными:
```bash
sudo docker-compose exec web python manage.py loaddata fixtures.json
```

### Альтернативный способ заполнения базы данными из фаилов cvs
***Работает только на пустой базе!***
```bash
sudo docker-compose exec web python manage.py data_import
```

## Доступ к YaMDb API

[http://62.113.114.234/api/v1/](http://62.113.114.234/api/v1/)

## Документация к YaMDb API

[http://62.113.114.234/redoc/](http://62.113.114.234/redoc/)

## Административная панель

[http://62.113.114.234/admin/](http://62.113.114.234/admin/)


## Примеры запросов к API

### Регистрация нового пользователя:
###### Доступно без токена

**POST**-запрос:

```http
http://62.113.114.234/api/v1/auth/signup/
```

Тело запроса:

```json
{
  "email": "new_user@test.ru",
  "username": "new_user"
}
```

Ответ:

```json
{
  "email": "new_user@test.ru",
  "username": "new_user"
}
```

Сообщение с токеном на email:
```
From: noreply@apiyamdb.ru
To: new_user@test.ru
Date: Mon, 26 Dec 2022 18:28:25 -0000

Ваш проверочный код rvKSy6rsRS.
```

---

### Получение списка всех жанров:
###### Доступно без токена

**GET**-запрос:

```http
http://62.113.114.234/api/v1/genres/
```

Ответ:

```json
{
    "count": 15,
    "next": "http://62.113.114.234/api/v1/genres/?page=2",
    "previous": null,
    "results": [
        {
            "name": "Rock-n-roll",
            "slug": "rock-n-roll"
        },
        {
            "name": "Баллада",
            "slug": "ballad"
        },
        {
            "name": "Вестерн",
            "slug": "western"
        },
        {
            "name": "Гонзо",
            "slug": "gonzo"
        },
        {
            "name": "Детектив",
            "slug": "detective"
        },
        {
            "name": "Драма",
            "slug": "drama"
        },
        {
            "name": "Классика",
            "slug": "classical"
        },
        {
            "name": "Комедия",
            "slug": "comedy"
        },
        {
            "name": "Рок",
            "slug": "rock"
        },
        {
            "name": "Роман",
            "slug": "roman"
        }
    ]
}
```

## Будущая доработка:
 * Отправка проверочного кода на электронную почту пользователя при регистрации.

## Авторы
1. Владислав Василенко ([vasilekx](https://github.com/vasilekx)) - управление пользователями
2. Писарева Светлана ([V0ronaVk0r0ne](https://github.com/V0ronaVk0r0ne)) - категории Categories, жанры Genres и произведения (Titles)
3. Виктор ([ViktorLuka](https://github.com/ViktorLuka)) - отзывы (Review) и комментарии (Comments)
