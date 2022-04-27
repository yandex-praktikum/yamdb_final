![example workflow](https://github.com/shdrn2402/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# YaMDb(docker-compose)

## О проекте:
**Проект YaMDb собирает отзывы (`Review`) пользователей на произведения (`Titles`).    
Произведения делятся на категории: «Книги», «Фильмы», «Музыка».**

### Запуск проекта:
#### 1. В dev-режиме:
Клонировать репозиторий и перейти в него в командной строке:
```sh
git clone git@github.com:shdrn2402/yamdb_final.git
```
Установить и активировать виртуальное окружение:
```sh
python -m venv venv
source venv/Scripts/activate
python -m pip install --upgrade pip
```
Установить зависимости из файла requirements.txt
```sh
pip install -r requirements.txt
```
Выполнить миграции:
```sh
python manage.py migrate
``` 
Импортировать данные:
```sh
python manage.py loaddata fixtures.json
```
или из CSV-файла:
```sh
python manage.py import_from_csv <csv файл> <название модели>
```
В папке с файлом manage.py выполните команду:
```sh
python manage.py runserver
```

#### 2. Запуск в контейнере docker:
Запустить `docker-compose` командой:
```
docker-compose up -d --build
```
Собрать статику и выполнить миграции внутри контейнера, создать суперпользователя:
```sh
docker-compose exec web python manage.py migrate --noinput
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
```
#### При необходимости возможно импортировать тестовые данные:
```sh
docker-compose exec web python manage.py loaddata fixtures.json
```
- При импорте создается суперюзер `admin` с паролем `admin`  и почтой `admin@yandex.ru`

### Ресурсы API YaMDb
- Ресурс `auth`: аутентификация.
- Ресурс `users`: пользователи.
- Ресурс `titles`: произведения, к которым пишут отзывы (определённый фильм, книга или песенка).
- Ресурс `categories`: категории (типы) произведений («Фильмы», «Книги», «Музыка»).
- Ресурс `genres`: жанры произведений. Одно произведение может быть привязано к нескольким жанрам.
- Ресурс `reviews`: отзывы на произведения. Отзыв привязан к определённому произведению.
- Ресурс `comments`: комментарии к отзывам. Комментарий привязан к определённому отзыву.

#### Подробную документацию можно посмотреть по [ссылке](http://127.0.0.1/redoc/) после запуска сервера с проектом.
