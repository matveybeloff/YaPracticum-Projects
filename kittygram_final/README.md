# Kittygram

Я собрал Kittygram — сервис, где владельцы котов делятся достижениями питомцев. Фронт на React, бэкенд на Django + PostgreSQL, всё упаковано в Docker.

## Что внутри
- API на Django REST Framework, авторизация через токены
- React-приложение, статикой и медиа заведует Nginx (gateway)
- Сборка и публикация образов в Docker Hub, автодеплой через GitHub Actions (`kittygram_workflow.yml`)

## Быстрый старт в Docker
1. В корне положите `.env`:
```
SECRET_KEY=your_secret_key
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
POSTGRES_DB=kittygram
POSTGRES_USER=kittygram
POSTGRES_PASSWORD=kittygram
DB_HOST=db
DB_PORT=5432
DOCKER_USERNAME=ваш_логин_на_Docker_Hub
```
2. Запустите стэк: `docker compose -f docker-compose.production.yml up -d`
3. Поднимите бэкенд:  
`docker compose -f docker-compose.production.yml exec backend python manage.py migrate`  
`docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput`  
`docker compose -f docker-compose.production.yml exec backend python manage.py createsuperuser`

Статика и медиа хранятся в общих томах `static` и `media`, gateway отдаёт их на порт 9000.

## Деплой на удалённый сервер
- Сервер с Docker и compose-plugin установлен. Клонирую репозиторий, копирую `.env` с боевыми секретами и доменами (`ALLOWED_HOSTS=example.com`). Если образы свои — меняю `DOCKER_USERNAME`.
- Обновление: `docker compose -f docker-compose.production.yml pull && docker compose -f docker-compose.production.yml up -d`
- Домен смотрит на gateway; по умолчанию проброшен порт `9000:80`, можно перекинуть на 80/443 или завернуть в внешний Nginx.

## Полезное
- Бэкенд без Docker можно поднять по инструкции в `backend/README.md`.
- После пуша в `main` CI собирает и выкладывает образы, а затем разворачивает их на сервере.
